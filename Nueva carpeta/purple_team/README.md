# Purple Team Framework v2.0

Professional cybersecurity operations platform for Purple Team exercises, combining Red Team offensive capabilities with Blue Team defensive monitoring.

> Inspired by the architecture of [ntopng](https://github.com/ntop/ntopng) — a high-performance, modular network monitoring application.

## Architecture

```
purple_team/
├── core/           # Core framework (config, crypto, database, logging, types)
├── c2/             # Command & Control server
├── agent/          # Agent system (payload execution, network scanning)
├── monitor/        # Network traffic monitoring & analysis
├── api/            # REST API server
├── chatbot/        # AI-powered cybersecurity assistant
├── waf/            # WAF management (Cloudflare integration)
├── web/            # Web dashboard (templates/static)
├── tests/          # Comprehensive test suite
├── configs/        # Configuration files (JSON schema)
├── data/           # Runtime data (DB, captures, knowledge base)
└── logs/           # Structured logging output
```

## Features

### 🎯 Command & Control (C2)
- Multi-threaded TCP/UDP server with auto-discovery
- Challenge-response authentication
- AES-256-GCM encrypted communications
- Key exchange via X25519 + HKDF
- Plugin-based module system
- Agent status tracking & persistence

### 🔍 Network Monitoring
- Real-time packet capture & analysis
- DPI (Deep Packet Inspection) ready
- Traffic flow tracking & export
- NetFlow v9 export support
- Anomaly detection engine
- Bandwidth monitoring by protocol/port/host

### 🛡️ WAF Management
- Cloudflare API integration
- IP blocking/challenge/allow rules
- Security events analysis
- Ruleset management
- Multi-zone support

### 🤖 Cybersecurity Chatbot
- Intent-based NLP classification
- Multi-provider AI support
- Knowledge base with security concepts
- Conversation history tracking
- Extensible command system

### 🔌 REST API
- HTTP/1.1 JSON API
- CORS support
- Authentication via API secret
- Full agent management
- Command execution & output retrieval
- Real-time stats & monitoring data

## Quick Start

### Installation

```bash
# Clone & install
pip install -r requirements.txt
pip install -e .

# Or with full features
pip install -e ".[full]"
```

### Start C2 Server

```bash
purple-team c2 start
```

### Scan a Target

```bash
purple-team scan 192.168.1.1 -p 1-1000
```

### Network Monitor

```bash
purple-team monitor start
purple-team monitor stats
```

### Start REST API

```bash
purple-team api start
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `c2 start/stop/status` | C2 server management |
| `scan <target>` | Port scan target |
| `ping <subnet>` | Ping sweep subnet |
| `monitor start/stop/stats` | Network monitoring |
| `agent list/info/command` | Agent management |
| `chatbot interactive/query` | AI assistant |
| `waf list/block/unblock` | WAF rule management |
| `api start/stop` | REST API server |
| `config show/set/save` | Configuration |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/status` | System status |
| `GET` | `/api/agents` | List agents |
| `GET` | `/api/agents/{id}` | Agent details |
| `POST` | `/api/agents/{id}/command` | Execute command |
| `POST` | `/api/agents/{id}/disconnect` | Disconnect agent |
| `GET` | `/api/agents/{id}/output` | Get command output |
| `GET` | `/api/alerts` | List alerts |
| `GET` | `/api/flows` | Network flows |
| `GET` | `/api/scans` | Scan results |
| `GET` | `/api/stats` | Dashboard stats |
| `POST` | `/api/scan` | Execute scan |

## Configuration

Configuration uses JSON files with hierarchical dot-notation access:

```bash
# View current config
purple-team config show

# Set a value
purple-team config set c2.tcp_port 5555

# Use custom config
purple-team --config my_config.json c2 start
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest purple_team/tests/ -v

# With coverage
pytest purple_team/tests/ --cov=purple_team -v

# Lint
black purple_team/

# Type check
mypy purple_team/
```

## Security

- All C2 communications encrypted with AES-256-GCM
- Challenge-response authentication prevents replay attacks
- X25519 key exchange with HKDF key derivation
- Configurable rate limiting and timeout
- Log rotation prevents disk exhaustion
- SQLite WAL mode for concurrent access

## License

MIT License - see LICENSE file for details.

---

Built for Purple Team operations. Use responsibly.
