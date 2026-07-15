import os
import json
from typing import Any, Dict, List, Optional
from pathlib import Path


class Config:
    _instance = None
    _data: Dict[str, Any] = {}

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, path: Optional[str] = None) -> None:
        paths = [
            path,
            os.getenv("PURPLE_TEAM_CONFIG"),
            str(Path(__file__).parent.parent / "configs" / "default.json"),
            str(Path(__file__).parent.parent.parent / "purple_team_config.json"),
        ]

        for p in filter(None, paths):
            p_expanded = os.path.expanduser(p)
            if os.path.exists(p_expanded):
                with open(p_expanded) as f:
                    self._data.update(json.load(f))
                return

        self._data = {**self._data, **self._defaults()}

    @staticmethod
    def _defaults() -> Dict[str, Any]:
        return {
            "c2": {
                "host": "0.0.0.0",
                "tcp_port": 5555,
                "udp_port": 5556,
                "http_port": 8080,
                "https_port": 8443,
                "password": "purple-team-2024",
                "max_attempts": 3,
                "timeout": 30,
                "broadcast_interval": 2,
                "rate_limit": 100,
                "ssl_cert": "",
                "ssl_key": "",
            },
            "agent": {
                "auto_discovery": True,
                "broadcast_listen": True,
                "reconnect_interval": 5,
                "max_retries": 20,
                "jitter": True,
                "kill_date": "",
                "encryption": True,
                "obfuscate": True,
            },
            "encryption": {
                "algorithm": "AES-256-GCM",
                "key_rotation_days": 7,
                "key_file": "~/.purple_team_key",
            },
            "logging": {
                "level": "INFO",
                "file": "logs/purple_team.log",
                "max_size_mb": 50,
                "backup_count": 5,
                "json_format": False,
            },
            "database": {
                "type": "sqlite",
                "path": "data/purple_team.db",
                "host": "",
                "port": 0,
                "user": "",
                "password": "",
            },
            "api": {
                "enabled": True,
                "host": "127.0.0.1",
                "port": 9090,
                "secret": "",
                "cors_origins": ["*"],
            },
            "chatbot": {
                "name": "Purple Team AI",
                "version": "2.0.0",
                "provider": "local",
                "model": "default",
            },
            "monitoring": {
                "enabled": True,
                "pcap_dir": "data/captures",
                "max_pcap_size_mb": 100,
                "flow_timeout": 300,
                "dpi_enabled": True,
            },
            "waf": {
                "cloudflare_email": "",
                "cloudflare_api_key": "",
                "auto_sync": False,
                "default_action": "block",
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        val = self._data
        try:
            for k in keys:
                val = val[k]
            return val
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        target = self._data
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value

    def save(self, path: Optional[str] = None) -> None:
        save_path = path or str(
            Path(__file__).parent.parent / "configs" / "default.json"
        )
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as f:
            json.dump(self._data, f, indent=2)

    @property
    def all(self) -> Dict[str, Any]:
        return self._data


config = Config()
