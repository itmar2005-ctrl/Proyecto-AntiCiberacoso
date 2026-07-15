import socket
import threading
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core.database import db
from ..core.logger import logger
from ..core.types import ScanResult


class Scanner:
    def __init__(self):
        self._running = False
        self._results: List[ScanResult] = []

    def scan(
        self,
        target: str,
        ports: str = "1-1024",
        timeout: float = 1.0,
        max_threads: int = 100,
    ) -> List[Dict[str, Any]]:
        self._running = True
        self._results = []

        port_range = self._parse_ports(ports)
        logger.info(f"Scanning {target} ports {port_range[0]}-{port_range[-1]}")

        threads = []
        semaphore = threading.Semaphore(max_threads)

        def scan_port(port: int) -> None:
            if not self._running:
                return
            with semaphore:
                result = self._scan_port(target, port, timeout)
                if result:
                    with threading.Lock():
                        self._results.append(result)
                        db.add_scan_result(result.to_dict())

        for port in port_range:
            t = threading.Thread(target=scan_port, args=(port,), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        logger.info(f"Scan complete: {len(self._results)} open ports found")
        self._running = False
        return [r.to_dict() for r in self._results]

    def _scan_port(
        self, target: str, port: int, timeout: float
    ) -> Optional[ScanResult]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            result = s.connect_ex((target, port))
            if result == 0:
                service = self._guess_service(port)
                banner = self._grab_banner(s, target, port)
                s.close()
                return ScanResult(
                    target=target,
                    port=port,
                    service=service,
                    state="open",
                    banner=banner,
                )
            s.close()
        except Exception:
            pass
        return None

    @staticmethod
    def _guess_service(port: int) -> str:
        common = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 135: "RPC",
            139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB",
            993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 1521: "Oracle",
            2049: "NFS", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
            5900: "VNC", 6379: "Redis", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt",
            27017: "MongoDB", 5060: "SIP", 161: "SNMP", 389: "LDAP",
            636: "LDAPS", 88: "Kerberos", 464: "Kerberos-Change",
            5555: "Purple-Team-C2", 5556: "Purple-Team-Discovery",
        }
        return common.get(port, "Unknown")

    @staticmethod
    def _grab_banner(sock: socket.socket, target: str, port: int) -> str:
        try:
            if port in (80, 443, 8080, 8443):
                sock.send(b"GET / HTTP/1.0\r\nHost: {target}\r\n\r\n")
            elif port == 22:
                pass
            sock.settimeout(3)
            banner = sock.recv(1024).decode("utf-8", errors="replace").strip()
            return banner[:200]
        except Exception:
            return ""

    @staticmethod
    def _parse_ports(ports: str) -> List[int]:
        result = []
        for part in ports.split(","):
            part = part.strip()
            if "-" in part:
                start, end = part.split("-", 1)
                result.extend(range(int(start), int(end) + 1))
            else:
                result.append(int(part))
        return result

    def stop(self) -> None:
        self._running = False

    def ping_sweep(self, subnet: str, timeout: float = 0.5) -> List[str]:
        active = []
        base = ".".join(subnet.split(".")[:-1])

        def ping(host: str) -> Optional[str]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(timeout)
                if s.connect_ex((host, 445)) == 0:
                    s.close()
                    return host
                s.close()
            except Exception:
                pass
            return None

        threads = []
        results = []

        for i in range(1, 255):
            host = f"{base}.{i}"
            t = threading.Thread(
                target=lambda h=host: results.append(ping(h)),
                daemon=True,
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return [r for r in results if r]

    def syn_scan(self, target: str, ports: str) -> List[Dict[str, Any]]:
        logger.info(f"SYN scan not implemented (requires raw sockets)")
        return self.scan(target, ports)
