from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from enum import Enum, auto
from datetime import datetime
from uuid import uuid4


class AgentStatus(Enum):
    OFFLINE = auto()
    ONLINE = auto()
    BUSY = auto()
    COMPROMISED = auto()
    CLEANED = auto()


class ModuleType(Enum):
    SCANNER = auto()
    SHELL = auto()
    KEYLOGGER = auto()
    WEBCAM = auto()
    MICROPHONE = auto()
    SCREENSHOT = auto()
    FILE_BROWSER = auto()
    PERSISTENCE = auto()
    NETWORK = auto()
    GPS = auto()
    CUSTOM = auto()


class AlertSeverity(Enum):
    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class AgentInfo:
    agent_id: str = field(default_factory=lambda: uuid4().hex[:12])
    hostname: str = ""
    username: str = ""
    os: str = ""
    ip: str = ""
    mac: str = ""
    status: AgentStatus = AgentStatus.OFFLINE
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.name.lower()
        d["first_seen"] = self.first_seen.isoformat()
        d["last_seen"] = self.last_seen.isoformat()
        return d


@dataclass
class Command:
    cmd_id: str = field(default_factory=lambda: uuid4().hex[:8])
    agent_id: str = ""
    command: str = ""
    args: List[str] = field(default_factory=list)
    timeout: int = 30
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    output: str = ""
    success: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        if self.executed_at:
            d["executed_at"] = self.executed_at.isoformat()
        return d


@dataclass
class NetworkFlow:
    src_ip: str = ""
    dst_ip: str = ""
    src_port: int = 0
    dst_port: int = 0
    protocol: str = ""
    bytes_sent: int = 0
    bytes_recv: int = 0
    packets: int = 0
    app_protocol: str = ""
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    duration: float = 0.0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["first_seen"] = self.first_seen.isoformat()
        d["last_seen"] = self.last_seen.isoformat()
        return d


@dataclass
class Alert:
    alert_id: str = field(default_factory=lambda: uuid4().hex[:12])
    severity: AlertSeverity = AlertSeverity.INFO
    title: str = ""
    description: str = ""
    source: str = ""
    agent_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["severity"] = self.severity.name.lower()
        d["timestamp"] = self.timestamp.isoformat()
        return d


@dataclass
class ScanResult:
    target: str = ""
    port: int = 0
    service: str = ""
    state: str = ""
    banner: str = ""
    vulnerabilities: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d
