#!/usr/bin/env python3
"""
Purple Team Framework v2.0
Professional cybersecurity operations platform
"""

import argparse
import sys
import os
import json
from typing import Optional

from .core.config import config
from .core.logger import logger, setup_logging
from .core.database import db
from .c2.server import c2_server
from .api.rest import api
from .agent.scanner import Scanner
from .monitor.sniffer import network_monitor
from .chatbot.engine import chatbot
from .waf.manager import waf_manager


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Purple Team Framework - Professional Cybersecurity Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  purple-team c2 --start              Start C2 server
  purple-team scan 192.168.1.1        Scan target
  purple-team monitor                 Start network monitoring
  purple-team chatbot                  Interactive chatbot session
  purple-team agent list              List connected agents
  purple-team waf block 1.2.3.4       Block IP via WAF
        """,
    )

    parser.add_argument(
        "--config", "-c", help="Path to configuration file", default=None
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging"
    )
    parser.add_argument(
        "--version", action="version", version="Purple Team Framework v2.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # `c2` command
    c2_parser = subparsers.add_parser("c2", help="C2 server operations")
    c2_parser.add_argument(
        "action",
        choices=["start", "stop", "status"],
        help="C2 server action",
    )
    c2_parser.add_argument("--host", help="Bind address")
    c2_parser.add_argument("--port", type=int, help="TCP port")
    c2_parser.add_argument("--udp-port", type=int, help="UDP port")

    # `scan` command
    scan_parser = subparsers.add_parser("scan", help="Network scanning")
    scan_parser.add_argument("target", help="Target IP or hostname")
    scan_parser.add_argument(
        "--ports", "-p", default="1-1024", help="Port range (e.g., 1-1000,80,443)"
    )
    scan_parser.add_argument("--timeout", type=float, default=1.0, help="Timeout per port")

    # `ping` command
    ping_parser = subparsers.add_parser("ping", help="Ping sweep subnet")
    ping_parser.add_argument("subnet", help="Subnet (e.g., 192.168.1.0)")
    ping_parser.add_argument("--timeout", type=float, default=0.5)

    # `monitor` command
    monitor_parser = subparsers.add_parser("monitor", help="Network monitoring")
    monitor_parser.add_argument("action", choices=["start", "stop", "status", "stats"])

    # `agent` command
    agent_parser = subparsers.add_parser("agent", help="Agent management")
    agent_parser.add_argument(
        "action", choices=["list", "info", "command", "disconnect"]
    )
    agent_parser.add_argument("--id", help="Agent ID")
    agent_parser.add_argument("--cmd", help="Command to execute")

    # `chatbot` command
    chatbot_parser = subparsers.add_parser("chatbot", help="Cybersecurity chatbot")
    chatbot_parser.add_argument(
        "action", choices=["start", "interactive", "query"]
    )
    chatbot_parser.add_argument("--message", "-m", help="Query message")

    # `waf` command
    waf_parser = subparsers.add_parser("waf", help="WAF management")
    waf_parser.add_argument("action", choices=["list", "block", "unblock", "status"])
    waf_parser.add_argument("--ip", help="Target IP")
    waf_parser.add_argument("--domain", help="Cloudflare domain")
    waf_parser.add_argument("--rule-id", help="Rule ID to delete")

    # `api` command
    api_parser = subparsers.add_parser("api", help="REST API server")
    api_parser.add_argument("action", choices=["start", "stop"])

    # `config` command
    config_parser = subparsers.add_parser("config", help="Configuration")
    config_parser.add_argument("action", choices=["show", "set", "save"])
    config_parser.add_argument("--key", help="Config key (e.g., c2.tcp_port)")
    config_parser.add_argument("--value", help="Config value")

    args = parser.parse_args()

    if args.config:
        config.load(args.config)
    else:
        config.load()

    if args.debug:
        setup_logging(level="DEBUG")
        logger.debug("Debug logging enabled")

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "c2": _handle_c2,
        "scan": _handle_scan,
        "ping": _handle_ping,
        "monitor": _handle_monitor,
        "agent": _handle_agent,
        "chatbot": _handle_chatbot,
        "waf": _handle_waf,
        "api": _handle_api,
        "config": _handle_config,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


def _handle_c2(args: argparse.Namespace) -> None:
    if args.host:
        config.set("c2.host", args.host)
    if args.port:
        config.set("c2.tcp_port", args.port)
    if args.udp_port:
        config.set("c2.udp_port", args.udp_port)

    if args.action == "start":
        c2_server.start()
        logger.info("C2 server started. Press Ctrl+C to stop.")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            c2_server.stop()
    elif args.action == "stop":
        c2_server.stop()
    elif args.action == "status":
        stats = c2_server.get_stats()
        print(json.dumps(stats, indent=2))


def _handle_scan(args: argparse.Namespace) -> None:
    scanner = Scanner()
    print(f"Scanning {args.target} (ports: {args.ports})...")
    results = scanner.scan(args.target, args.ports, args.timeout)
    if results:
        print(f"\n{'PORT':<8} {'STATE':<8} {'SERVICE':<12} BANNER")
        print("-" * 60)
        for r in results:
            banner = r.get("banner", "")[:40]
            print(f"{r['port']:<8} {r['state']:<8} {r['service']:<12} {banner}")
    else:
        print("No open ports found.")


def _handle_ping(args: argparse.Namespace) -> None:
    scanner = Scanner()
    print(f"Ping sweep of {args.subnet}.0/24...")
    active = scanner.ping_sweep(args.subnet, args.timeout)
    if active:
        print(f"\nActive hosts ({len(active)}):")
        for host in sorted(active):
            print(f"  {host}")
    else:
        print("No active hosts found.")


def _handle_monitor(args: argparse.Namespace) -> None:
    if args.action == "start":
        network_monitor.start()
        logger.info("Network monitor started")
    elif args.action == "stop":
        network_monitor.stop()
        logger.info("Network monitor stopped")
    elif args.action == "status":
        data = network_monitor.get_dashboard_data()
        print(json.dumps(data, indent=2, default=str))
    elif args.action == "stats":
        stats = network_monitor.sniffer.get_stats()
        print(json.dumps(stats, indent=2, default=str))


def _handle_agent(args: argparse.Namespace) -> None:
    if args.action == "list":
        agents = c2_server.list_agents()
        if agents:
            print(f"{'ID':<20} {'HOSTNAME':<20} {'IP':<16} {'STATUS':<12} {'OS':<12}")
            print("-" * 80)
            for a in agents:
                print(
                    f"{a.get('agent_id', '?'):<20} "
                    f"{a.get('hostname', '?'):<20} "
                    f"{a.get('ip', '?'):<16} "
                    f"{a.get('status', '?'):<12} "
                    f"{a.get('os', '?'):<12}"
                )
        else:
            print("No agents connected.")
    elif args.action == "info":
        if not args.id:
            print("Error: --id required")
            return
        agent = c2_server.get_agent(args.id)
        if agent:
            print(json.dumps(agent, indent=2, default=str))
        else:
            print(f"Agent {args.id} not found.")
    elif args.action == "command":
        if not args.id or not args.cmd:
            print("Error: --id and --cmd required")
            return
        success = c2_server.send_command(args.id, args.cmd)
        if success:
            import time
            time.sleep(1)
            output = c2_server.get_cmd_buffer(args.id, clear=True)
            print(output or "Command sent (no output yet)")
        else:
            print(f"Failed to send command to {args.id}")
    elif args.action == "disconnect":
        if not args.id:
            print("Error: --id required")
            return
        c2_server.disconnect_agent(args.id)
        print(f"Agent {args.id} disconnected.")


def _handle_chatbot(args: argparse.Namespace) -> None:
    if args.action in ("start", "interactive"):
        print(f"Chatbot {chatbot.name} v{chatbot.version}")
        print("Type 'exit' to quit, 'help' for commands\n")
        while True:
            try:
                msg = input("> ").strip()
                if msg.lower() in ("exit", "quit", "salir"):
                    break
                response = chatbot.chat(msg)
                print(response)
            except (EOFError, KeyboardInterrupt):
                break
    elif args.action == "query":
        if not args.message:
            print("Error: --message required")
            return
        response = chatbot.chat(args.message)
        print(response)


def _handle_waf(args: argparse.Namespace) -> None:
    if args.action == "list":
        domain = args.domain or ""
        rules = waf_manager.list_rules(domain)
        if rules:
            print(f"{'ID':<40} {'ACTION':<12} {'EXPRESSION':<40}")
            print("-" * 92)
            for r in rules:
                print(
                    f"{r.get('id', '?'):<40} "
                    f"{r.get('action', '?'):<12} "
                    f"{r.get('expression', '?'):<40}"
                )
        else:
            print("No WAF rules found.")
    elif args.action == "block":
        if not args.ip:
            print("Error: --ip required")
            return
        domain = args.domain or ""
        result = waf_manager.block_ip(domain, args.ip)
        if result:
            print(f"IP {args.ip} blocked successfully.")
        else:
            print(f"Failed to block {args.ip}.")
    elif args.action == "unblock":
        if not args.rule_id:
            print("Error: --rule-id required")
            return
        domain = args.domain or ""
        waf_manager.delete_rule(domain, args.rule_id)
        print(f"Rule {args.rule_id} deleted.")
    elif args.action == "status":
        domain = args.domain or ""
        report = waf_manager.generate_report(domain)
        print(json.dumps(report, indent=2, default=str))


def _handle_api(args: argparse.Namespace) -> None:
    if args.action == "start":
        api.start()
        logger.info(f"REST API started on {api._host}:{api._port}")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            api.stop()
    elif args.action == "stop":
        api.stop()


def _handle_config(args: argparse.Namespace) -> None:
    if args.action == "show":
        print(json.dumps(config.all, indent=2))
    elif args.action == "set":
        if not args.key or not args.value:
            print("Error: --key and --value required")
            return
        val = args.value
        try:
            val = json.loads(val)
        except (json.JSONDecodeError, ValueError):
            pass
        config.set(args.key, val)
        print(f"  {args.key} = {json.dumps(val)}")
    elif args.action == "save":
        config.save()
        print("Configuration saved.")


if __name__ == "__main__":
    main()
