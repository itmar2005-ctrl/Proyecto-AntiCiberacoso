import pytest
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfig:
    def test_defaults(self):
        from purple_team.core.config import config
        config.load(os.devnull)
        assert config.get("c2.tcp_port") == 5555
        assert config.get("c2.udp_port") == 5556
        assert config.get("logging.level") == "INFO"

    def test_set_and_get(self):
        from purple_team.core.config import config
        config.set("test.key", "value")
        assert config.get("test.key") == "value"

    def test_nested_key(self):
        from purple_team.core.config import config
        assert config.get("c2.host") == "0.0.0.0"

    def test_missing_key(self):
        from purple_team.core.config import config
        assert config.get("nonexistent.key") is None
        assert config.get("nonexistent", "default") == "default"


class TestCrypto:
    def test_encrypt_decrypt(self):
        from purple_team.core.crypto import CryptoEngine
        crypto = CryptoEngine(key=b"0" * 32)
        data = b"test data"
        encrypted = crypto.encrypt(data)
        decrypted = crypto.decrypt(encrypted)
        assert decrypted == data

    def test_encrypt_dict(self):
        from purple_team.core.crypto import CryptoEngine
        crypto = CryptoEngine(key=b"0" * 32)
        data = {"key": "value", "number": 42}
        encrypted = crypto.encrypt_dict(data)
        decrypted = crypto.decrypt_dict(encrypted)
        assert decrypted == data

    def test_aes_gcm(self):
        from purple_team.core.crypto import CryptoEngine
        key = b"0" * 32
        data = b"secret message"
        nonce, ct = CryptoEngine.encrypt_aes_gcm(key, data)
        decrypted = CryptoEngine.decrypt_aes_gcm(key, nonce, ct)
        assert decrypted == data


class TestDatabase:
    @pytest.fixture
    def db(self):
        from purple_team.core.database import Database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        db = Database(db_path)
        yield db
        db.close()
        os.unlink(db_path)

    def test_upsert_agent(self, db):
        db.upsert_agent({
            "agent_id": "test-agent",
            "hostname": "test-pc",
            "username": "test",
            "os": "Windows",
            "ip": "192.168.1.100",
            "status": "online",
        })
        agent = db.get_agent("test-agent")
        assert agent is not None
        assert agent["hostname"] == "test-pc"
        assert agent["ip"] == "192.168.1.100"

    def test_list_agents(self, db):
        db.upsert_agent({"agent_id": "a1", "hostname": "h1", "status": "online"})
        db.upsert_agent({"agent_id": "a2", "hostname": "h2", "status": "offline"})
        agents = db.list_agents()
        assert len(agents) == 2

    def test_add_command(self, db):
        db.add_command({
            "cmd_id": "cmd1",
            "agent_id": "a1",
            "command": "whoami",
            "timeout": 30,
        })
        cmds = db.get_pending_commands("a1")
        assert len(cmds) == 1
        assert cmds[0]["command"] == "whoami"

    def test_add_alert(self, db):
        db.add_alert({
            "alert_id": "alert1",
            "severity": "high",
            "title": "Test Alert",
            "description": "Test description",
        })
        alerts = db.list_alerts()
        assert len(alerts) >= 1

    def test_add_flow(self, db):
        db.add_flow({
            "src_ip": "10.0.0.1",
            "dst_ip": "10.0.0.2",
            "src_port": 1234,
            "dst_port": 80,
            "protocol": "TCP",
            "bytes_sent": 1024,
        })
        flows = db.get_flows()
        assert len(flows) >= 1

    def test_add_scan_result(self, db):
        db.add_scan_result({
            "target": "192.168.1.1",
            "port": 80,
            "service": "HTTP",
            "state": "open",
        })
        results = db.get_scan_results()
        assert len(results) >= 1

    def test_get_stats(self, db):
        stats = db.get_stats()
        assert "agents_online" in stats
        assert "alerts_critical" in stats


class TestScanner:
    def test_parse_ports(self):
        from purple_team.agent.scanner import Scanner
        scanner = Scanner()
        ports = scanner._parse_ports("80,443,3000-3005")
        assert 80 in ports
        assert 443 in ports
        assert 3000 in ports
        assert 3005 in ports
        assert len(ports) == 8

    def test_guess_service(self):
        from purple_team.agent.scanner import Scanner
        assert Scanner._guess_service(22) == "SSH"
        assert Scanner._guess_service(80) == "HTTP"
        assert Scanner._guess_service(443) == "HTTPS"
        assert Scanner._guess_service(3389) == "RDP"
        assert Scanner._guess_service(9999) == "Unknown"


class TestTypes:
    def test_agent_info(self):
        from purple_team.core.types import AgentInfo, AgentStatus
        a = AgentInfo(
            agent_id="test",
            hostname="host",
            username="user",
            os="Linux",
            ip="10.0.0.1",
        )
        d = a.to_dict()
        assert d["agent_id"] == "test"
        assert d["hostname"] == "host"
        assert d["status"] == "offline"

    def test_command(self):
        from purple_team.core.types import Command
        c = Command(agent_id="a1", command="ls -la")
        assert c.cmd_id is not None
        d = c.to_dict()
        assert d["agent_id"] == "a1"
        assert d["command"] == "ls -la"

    def test_alert_severity(self):
        from purple_team.core.types import Alert, AlertSeverity
        a = Alert(
            severity=AlertSeverity.CRITICAL,
            title="Critical Alert",
            source="test",
        )
        d = a.to_dict()
        assert d["severity"] == "critical"
        assert d["title"] == "Critical Alert"


class TestChatbot:
    @pytest.fixture
    def bot(self):
        from purple_team.chatbot.engine import ChatbotEngine
        return ChatbotEngine()

    def test_help(self, bot):
        response = bot.chat("help")
        assert "Comandos disponibles" in response

    def test_greeting(self, bot):
        response = bot.chat("hola")
        assert "Purple Team" in response

    def test_unknown(self, bot):
        response = bot.chat("xyzzy")
        assert "No entendí" in response

    def test_status(self, bot):
        response = bot.chat("status")
        assert "Estado del Sistema" in response

    def test_reset(self, bot):
        response = bot.reset_conversation()
        assert "reiniciada" in response


class TestWAF:
    def test_ip_reputation(self):
        from purple_team.waf.manager import IPReputation
        rep = IPReputation()
        result = rep.check_ip("8.8.8.8")
        assert result["ip"] == "8.8.8.8"
        assert "geo" in result


class TestNetworkStats:
    def test_traffic_stats(self):
        from purple_team.monitor.sniffer import TrafficStats
        stats = TrafficStats()
        stats.total_bytes = 1000
        stats.total_packets = 100
        stats.flows = 10
        d = stats.to_dict()
        assert d["total_bytes"] == 1000
        assert d["total_packets"] == 100
        assert d["flows"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
