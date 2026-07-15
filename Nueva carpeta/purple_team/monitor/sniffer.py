import socket
import struct
import threading
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field

from ..core.config import config
from ..core.logger import logger
from ..core.database import db
from ..core.types import NetworkFlow, Alert, AlertSeverity


@dataclass
class TrafficStats:
    total_bytes: int = 0
    total_packets: int = 0
    tcp_bytes: int = 0
    udp_bytes: int = 0
    icmp_bytes: int = 0
    flows: int = 0
    active_connections: int = 0
    top_talkers: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    top_ports: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    top_protocols: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_bytes": self.total_bytes,
            "total_packets": self.total_packets,
            "tcp_bytes": self.tcp_bytes,
            "udp_bytes": self.udp_bytes,
            "flows": self.flows,
            "active_connections": self.active_connections,
            "top_talkers": dict(
                sorted(self.top_talkers.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "top_ports": dict(
                sorted(self.top_ports.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "top_protocols": dict(
                sorted(self.top_protocols.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
        }


class PacketSniffer:
    def __init__(self, interface: Optional[str] = None):
        self._interface = interface
        self._running = False
        self._stats = TrafficStats()
        self._active_flows: Dict[str, NetworkFlow] = {}
        self._lock = threading.Lock()
        self._alerts_enabled = True
        self._dpi_enabled = config.get("monitoring.dpi_enabled", True)
        self._flow_timeout = config.get("monitoring.flow_timeout", 300)

    def start(self) -> None:
        self._running = True
        thread = threading.Thread(target=self._capture_loop, daemon=True)
        thread.start()
        logger.info(
            f"Packet sniffer started on interface: {self._interface or 'default'}"
        )

    def stop(self) -> None:
        self._running = False
        self._flush_flows()
        logger.info("Packet sniffer stopped")

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return self._stats.to_dict()

    def get_flows(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            sorted_flows = sorted(
                self._active_flows.values(),
                key=lambda f: f.last_seen,
                reverse=True,
            )
            return [f.to_dict() for f in sorted_flows[:limit]]

    def _capture_loop(self) -> None:
        import platform

        if platform.system() == "Windows":
            self._capture_windows()
        else:
            self._capture_linux()

    def _capture_windows(self) -> None:
        logger.info("Windows packet capture via PowerShell counters")
        while self._running:
            try:
                import subprocess
                result = subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        "Get-NetAdapterStatistics | ConvertTo-Json",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    self._update_stats_from_json(result.stdout)
            except Exception as e:
                logger.debug(f"Win capture: {e}")
            time.sleep(5)

    def _capture_linux(self) -> None:
        logger.info("Linux packet capture via scapy")
        try:
            from scapy.all import sniff
            sniff(iface=self._interface, prn=self._process_packet, store=0, stop_filter=lambda p: not self._running)
        except ImportError:
            logger.warning("scapy not installed, using procfs")
            self._capture_procfs()
        except Exception as e:
            logger.error(f"Sniff error: {e}")

    def _capture_procfs(self) -> None:
        last_rx, last_tx = 0, 0
        while self._running:
            try:
                with open("/proc/net/dev") as f:
                    for line in f:
                        if ":" in line:
                            parts = line.split()
                            iface = parts[0].rstrip(":")
                            if self._interface and iface != self._interface:
                                continue
                            rx = int(parts[1])
                            tx = int(parts[9])
                            if last_rx > 0:
                                with self._lock:
                                    self._stats.total_bytes += (rx - last_rx) + (tx - last_tx)
                                    self._stats.total_packets += int(parts[2]) - last_rx
                            last_rx, last_tx = rx, tx
            except Exception:
                pass
            time.sleep(2)

    def _update_stats_from_json(self, json_str: str) -> None:
        import json
        try:
            data = json.loads(json_str)
            if isinstance(data, list):
                for iface in data:
                    if self._interface and iface.get("Name") != self._interface:
                        continue
                    with self._lock:
                        self._stats.total_bytes += iface.get("BytesReceived", 0) + iface.get("BytesSent", 0)
                        self._stats.total_packets += iface.get("PacketsReceived", 0) + iface.get("PacketsSent", 0)
                        self._stats.active_connections = iface.get("ActiveConnections", 0)
        except Exception:
            pass

    def _process_packet(self, packet: Any) -> None:
        if not self._running:
            return
        try:
            if hasattr(packet, "haslayer"):
                from scapy.layers.inet import IP, TCP, UDP, ICMP

                if not packet.haslayer(IP):
                    return

                ip = packet[IP]
                src, dst = ip.src, ip.dst
                proto = ip.proto
                size = len(packet)
                proto_name = {1: "ICMP", 6: "TCP", 17: "UDP"}.get(proto, f"IP-{proto}")

                flow_key = f"{src}:{dst}"
                if packet.haslayer(TCP):
                    tcp = packet[TCP]
                    flow_key = f"{src}:{tcp.sport}-{dst}:{tcp.dport}"
                    with self._lock:
                        self._stats.tcp_bytes += size
                elif packet.haslayer(UDP):
                    udp = packet[UDP]
                    flow_key = f"{src}:{udp.sport}-{dst}:{udp.dport}"
                    with self._lock:
                        self._stats.udp_bytes += size
                elif packet.haslayer(ICMP):
                    with self._lock:
                        self._stats.icmp_bytes += size

                with self._lock:
                    self._stats.total_bytes += size
                    self._stats.total_packets += 1
                    self._stats.top_talkers[src] += size
                    self._stats.top_talkers[dst] += size

                    if flow_key not in self._active_flows:
                        flow = NetworkFlow(
                            src_ip=src,
                            dst_ip=dst,
                            src_port=getattr(packet[TCP], "sport", 0) if packet.haslayer(TCP) else 0,
                            dst_port=getattr(packet[TCP], "dport", 0) if packet.haslayer(TCP) else 0,
                            protocol=proto_name,
                        )
                        self._active_flows[flow_key] = flow
                        self._stats.flows += 1
                    else:
                        flow = self._active_flows[flow_key]
                        flow.bytes_sent += size
                        flow.packets += 1
                        flow.last_seen = datetime.utcnow()
                        flow.duration = (flow.last_seen - flow.first_seen).total_seconds()

        except Exception as e:
            logger.debug(f"Packet processing error: {e}")

    def _flush_flows(self) -> None:
        with self._lock:
            now = datetime.utcnow()
            to_remove = []
            for key, flow in self._active_flows.items():
                if (now - flow.last_seen).total_seconds() > self._flow_timeout:
                    db.add_flow(flow.to_dict())
                    to_remove.append(key)
            for key in to_remove:
                del self._active_flows[key]

    def analyze_dns(self, packet: Any) -> Optional[Dict[str, Any]]:
        try:
            if hasattr(packet, "haslayer"):
                from scapy.layers.dns import DNS, DNSQR
                if packet.haslayer(DNS) and packet.haslayer(DNSQR):
                    dns = packet[DNS]
                    qr = packet[DNSQR]
                    return {
                        "query": qr.qname.decode() if isinstance(qr.qname, bytes) else str(qr.qname),
                        "type": qr.qtype,
                        "response": dns.an.rdata if dns.an else None,
                    }
        except Exception:
            pass
        return None

    def analyze_http(self, packet: Any) -> Optional[Dict[str, Any]]:
        try:
            if hasattr(packet, "haslayer") and hasattr(packet, "load"):
                load = bytes(packet.load) if hasattr(packet, "load") else b""
                if b"HTTP/" in load:
                    lines = load.decode("utf-8", errors="replace").split("\r\n")
                    if lines:
                        request = lines[0]
                        parts = request.split(" ")
                        if len(parts) >= 2:
                            return {
                                "method": parts[0],
                                "path": parts[1],
                                "host": next((l.split(": ", 1)[1] for l in lines if l.lower().startswith("host:")), ""),
                            }
        except Exception:
            pass
        return None

    def check_anomalies(self, packet: Any) -> Optional[Alert]:
        try:
            if hasattr(packet, "haslayer"):
                from scapy.layers.inet import IP, TCP
                if packet.haslayer(IP) and packet.haslayer(TCP):
                    ip = packet[IP]
                    tcp = packet[TCP]
                    if tcp.flags & 0x29:
                        pass
                    if len(packet) > 1500:
                        return Alert(
                            severity=AlertSeverity.MEDIUM,
                            title="Jumbo Frame Detected",
                            description=f"Packet size: {len(packet)} bytes from {ip.src}",
                            source="packet_sniffer",
                        )
        except Exception:
            pass
        return None


class FlowExporter:
    def __init__(self):
        self._exporters: Dict[str, Any] = {}

    def register_exporter(self, name: str, exporter: Any) -> None:
        self._exporters[name] = exporter

    def export_flows(self, flows: List[Dict[str, Any]], format: str = "json") -> str:
        if format == "json":
            import json
            return json.dumps(flows, indent=2)
        elif format == "csv":
            import csv
            import io
            output = io.StringIO()
            if flows:
                writer = csv.DictWriter(output, fieldnames=flows[0].keys())
                writer.writeheader()
                writer.writerows(flows)
            return output.getvalue()
        elif format == "netflow":
            return self._export_netflow_v9(flows)
        return str(flows)

    @staticmethod
    def _export_netflow_v9(flows: List[Dict[str, Any]]) -> str:
        template_id = 256
        packet = bytearray()
        packet.extend(struct.pack("!H", 9))
        packet.extend(struct.pack("!H", len(flows)))
        packet.extend(b"\x00" * 4)
        now = int(time.time())
        packet.extend(struct.pack("!I", now))
        packet.extend(struct.pack("!I", now + 300))
        for flow in flows[:30]:
            packet.extend(socket.inet_aton(flow.get("src_ip", "0.0.0.0")))
            packet.extend(socket.inet_aton(flow.get("dst_ip", "0.0.0.0")))
            packet.extend(struct.pack("!I", flow.get("bytes_sent", 0)))
            packet.extend(struct.pack("!I", flow.get("packets", 0)))
            packet.extend(struct.pack("!HH", flow.get("src_port", 0), flow.get("dst_port", 0)))
            packet.extend(struct.pack("!B", {6: 6, 17: 17}.get(flow.get("protocol", ""), 0)))
        return bytes(packet).hex()


class NetworkMonitor:
    def __init__(self):
        self.sniffer = PacketSniffer()
        self.exporter = FlowExporter()
        self._running = False

    def start(self) -> None:
        self._running = True
        self.sniffer.start()
        logger.info("Network monitor started")

    def stop(self) -> None:
        self._running = False
        self.sniffer.stop()

    def get_dashboard_data(self) -> Dict[str, Any]:
        return {
            "stats": self.sniffer.get_stats(),
            "flows": self.sniffer.get_flows(limit=20),
            "timestamp": datetime.utcnow().isoformat(),
        }


network_monitor = NetworkMonitor()
