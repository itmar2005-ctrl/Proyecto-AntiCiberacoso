import sqlite3
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

from .config import config


class Database:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or str(
            Path(__file__).parent.parent / config.get("database.path", "data/purple_team.db")
        )
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._init_tables()

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_tables(self) -> None:
        with self._get_conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    hostname TEXT,
                    username TEXT,
                    os TEXT,
                    ip TEXT,
                    mac TEXT,
                    status TEXT DEFAULT 'offline',
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags TEXT DEFAULT '[]',
                    modules TEXT DEFAULT '[]'
                );
                CREATE TABLE IF NOT EXISTS commands (
                    cmd_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    command TEXT NOT NULL,
                    args TEXT DEFAULT '[]',
                    timeout INTEGER DEFAULT 30,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    executed_at TIMESTAMP,
                    output TEXT DEFAULT '',
                    success INTEGER DEFAULT 0,
                    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
                );
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id TEXT PRIMARY KEY,
                    severity TEXT DEFAULT 'info',
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    source TEXT DEFAULT '',
                    agent_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    acknowledged INTEGER DEFAULT 0,
                    data TEXT DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS network_flows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    src_ip TEXT,
                    dst_ip TEXT,
                    src_port INTEGER,
                    dst_port INTEGER,
                    protocol TEXT,
                    bytes_sent INTEGER DEFAULT 0,
                    bytes_recv INTEGER DEFAULT 0,
                    packets INTEGER DEFAULT 0,
                    app_protocol TEXT DEFAULT '',
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    duration REAL DEFAULT 0.0,
                    tags TEXT DEFAULT '[]'
                );
                CREATE TABLE IF NOT EXISTS scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT,
                    port INTEGER,
                    service TEXT,
                    state TEXT,
                    banner TEXT DEFAULT '',
                    vulnerabilities TEXT DEFAULT '[]',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    bytes_transferred INTEGER DEFAULT 0,
                    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
                );
            """
            )

    def upsert_agent(self, agent: Dict[str, Any]) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO agents (agent_id, hostname, username, os, ip, mac, status, last_seen, tags, modules)
                   VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
                   ON CONFLICT(agent_id) DO UPDATE SET
                       hostname=excluded.hostname, username=excluded.username,
                       os=excluded.os, ip=excluded.ip, mac=excluded.mac,
                       status=excluded.status, last_seen=CURRENT_TIMESTAMP,
                       tags=excluded.tags, modules=excluded.modules""",
                (
                    agent["agent_id"],
                    agent.get("hostname", ""),
                    agent.get("username", ""),
                    agent.get("os", ""),
                    agent.get("ip", ""),
                    agent.get("mac", ""),
                    agent.get("status", "online"),
                    json.dumps(agent.get("tags", [])),
                    json.dumps(agent.get("modules", [])),
                ),
            )

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM agents WHERE agent_id = ?", (agent_id,)
            ).fetchone()
            if row:
                d = dict(row)
                d["tags"] = json.loads(d["tags"])
                d["modules"] = json.loads(d["modules"])
                return d
        return None

    def list_agents(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM agents WHERE status = ? ORDER BY last_seen DESC", (status,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM agents ORDER BY last_seen DESC"
                ).fetchall()
            result = []
            for row in rows:
                d = dict(row)
                d["tags"] = json.loads(d["tags"])
                d["modules"] = json.loads(d["modules"])
                result.append(d)
            return result

    def add_command(self, cmd: Dict[str, Any]) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO commands (cmd_id, agent_id, command, args, timeout, created_at)
                   VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (
                    cmd["cmd_id"],
                    cmd["agent_id"],
                    cmd["command"],
                    json.dumps(cmd.get("args", [])),
                    cmd.get("timeout", 30),
                ),
            )

    def update_command(self, cmd_id: str, output: str, success: bool) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """UPDATE commands SET output=?, success=?, executed_at=CURRENT_TIMESTAMP
                   WHERE cmd_id=?""",
                (output, 1 if success else 0, cmd_id),
            )

    def get_pending_commands(self, agent_id: str) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM commands WHERE agent_id=? AND executed_at IS NULL ORDER BY created_at ASC",
                (agent_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def add_alert(self, alert: Dict[str, Any]) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO alerts (alert_id, severity, title, description, source, agent_id, timestamp, data)
                   VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)""",
                (
                    alert["alert_id"],
                    alert.get("severity", "info"),
                    alert["title"],
                    alert.get("description", ""),
                    alert.get("source", ""),
                    alert.get("agent_id"),
                    json.dumps(alert.get("data", {})),
                ),
            )

    def list_alerts(
        self, limit: int = 50, severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            if severity:
                rows = conn.execute(
                    "SELECT * FROM alerts WHERE severity=? ORDER BY timestamp DESC LIMIT ?",
                    (severity, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?", (limit,)
                ).fetchall()
            result = []
            for row in rows:
                d = dict(row)
                d["data"] = json.loads(d["data"]) if d["data"] else {}
                result.append(d)
            return result

    def add_flow(self, flow: Dict[str, Any]) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO network_flows (src_ip, dst_ip, src_port, dst_port, protocol,
                   bytes_sent, bytes_recv, packets, app_protocol, duration, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    flow["src_ip"],
                    flow["dst_ip"],
                    flow.get("src_port", 0),
                    flow.get("dst_port", 0),
                    flow.get("protocol", ""),
                    flow.get("bytes_sent", 0),
                    flow.get("bytes_recv", 0),
                    flow.get("packets", 0),
                    flow.get("app_protocol", ""),
                    flow.get("duration", 0.0),
                    json.dumps(flow.get("tags", [])),
                ),
            )

    def get_flows(
        self, limit: int = 100, src_ip: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            if src_ip:
                rows = conn.execute(
                    "SELECT * FROM network_flows WHERE src_ip=? OR dst_ip=? ORDER BY last_seen DESC LIMIT ?",
                    (src_ip, src_ip, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM network_flows ORDER BY last_seen DESC LIMIT ?", (limit,)
                ).fetchall()
            result = []
            for row in rows:
                d = dict(row)
                d["tags"] = json.loads(d["tags"]) if d["tags"] else []
                result.append(d)
            return result

    def add_scan_result(self, scan: Dict[str, Any]) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO scan_results (target, port, service, state, banner, vulnerabilities)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    scan["target"],
                    scan.get("port", 0),
                    scan.get("service", ""),
                    scan.get("state", ""),
                    scan.get("banner", ""),
                    json.dumps(scan.get("vulnerabilities", [])),
                ),
            )

    def get_scan_results(self, target: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            if target:
                rows = conn.execute(
                    "SELECT * FROM scan_results WHERE target=? ORDER BY timestamp DESC",
                    (target,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM scan_results ORDER BY timestamp DESC"
                ).fetchall()
            result = []
            for row in rows:
                d = dict(row)
                d["vulnerabilities"] = json.loads(d["vulnerabilities"]) if d["vulnerabilities"] else []
                result.append(d)
            return result

    def get_stats(self) -> Dict[str, Any]:
        with self._get_conn() as conn:
            agents_online = conn.execute(
                "SELECT COUNT(*) FROM agents WHERE status='online'"
            ).fetchone()[0]
            agents_total = conn.execute(
                "SELECT COUNT(*) FROM agents"
            ).fetchone()[0]
            alerts_critical = conn.execute(
                "SELECT COUNT(*) FROM alerts WHERE severity='critical' AND acknowledged=0"
            ).fetchone()[0]
            commands_pending = conn.execute(
                "SELECT COUNT(*) FROM commands WHERE executed_at IS NULL"
            ).fetchone()[0]
            flows_total = conn.execute(
                "SELECT COUNT(*) FROM network_flows"
            ).fetchone()[0]
            return {
                "agents_online": agents_online,
                "agents_total": agents_total,
                "alerts_critical": alerts_critical,
                "commands_pending": commands_pending,
                "flows_total": flows_total,
            }

    def close(self) -> None:
        pass


db = Database()
