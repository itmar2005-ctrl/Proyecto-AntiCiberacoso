import json
import socket
import threading
from typing import Any, Dict, Optional
from urllib.parse import parse_qs

from ..core.config import config
from ..core.logger import logger
from ..core.database import db
from ..c2.server import c2_server


class RESTAPI:
    def __init__(self):
        self._host = config.get("api.host", "127.0.0.1")
        self._port = config.get("api.port", 9090)
        self._secret = config.get("api.secret", "")
        self._server: Optional[socket.socket] = None
        self._running = False
        self._routes: Dict[str, Dict[str, callable]] = {}

    def _route(self, method: str, path: str, handler: callable) -> None:
        if path not in self._routes:
            self._routes[path] = {}
        self._routes[path][method.upper()] = handler

    def start(self) -> None:
        import socket

        self._running = True
        self._register_routes()

        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._server.bind((self._host, self._port))
            self._server.listen(10)
            self._server.settimeout(1)
        except Exception as e:
            logger.error(f"API bind failed: {e}")
            return

        thread = threading.Thread(target=self._serve, daemon=True)
        thread.start()
        logger.info(f"REST API listening on {self._host}:{self._port}")

    def stop(self) -> None:
        self._running = False
        if self._server:
            try:
                self._server.close()
            except Exception:
                pass

    def _register_routes(self) -> None:
        self._route("GET", "/api/status", self._handle_status)
        self._route("GET", "/api/agents", self._handle_list_agents)
        self._route("GET", "/api/agents/{id}", self._handle_get_agent)
        self._route("POST", "/api/agents/{id}/command", self._handle_send_command)
        self._route("POST", "/api/agents/{id}/disconnect", self._handle_disconnect)
        self._route("GET", "/api/agents/{id}/output", self._handle_get_output)
        self._route("GET", "/api/alerts", self._handle_list_alerts)
        self._route("GET", "/api/flows", self._handle_list_flows)
        self._route("GET", "/api/scans", self._handle_list_scans)
        self._route("GET", "/api/stats", self._handle_stats)
        self._route("POST", "/api/scan", self._handle_scan)

    def _serve(self) -> None:
        import socket

        while self._running:
            try:
                conn, addr = self._server.accept()
                thread = threading.Thread(
                    target=self._handle_request, args=(conn,), daemon=True
                )
                thread.start()
            except socket.timeout:
                continue
            except Exception:
                if self._running:
                    logger.exception("API accept error")

    def _handle_request(self, conn: socket.socket) -> None:
        try:
            conn.settimeout(10)
            data = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\r\n\r\n" in data:
                    break

            if not data:
                conn.close()
                return

            request_line = data.split(b"\r\n")[0].decode()
            parts = request_line.split(" ")
            if len(parts) < 2:
                conn.close()
                return

            method, path = parts[0], parts[1].split("?")[0]
            query_string = parts[1].split("?")[1] if "?" in parts[1] else ""
            query_params = parse_qs(query_string)
            body_start = data.find(b"\r\n\r\n") + 4
            body = data[body_start:].decode() if data[body_start:] else "{}"

            try:
                json_body = json.loads(body) if body else {}
            except json.JSONDecodeError:
                json_body = {}

            response = self._route_request(method, path, query_params, json_body)
            self._send_response(conn, response)

        except Exception as e:
            logger.error(f"API request error: {e}")
            self._send_response(
                conn, {"status": 500, "body": {"error": str(e)}}
            )
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _route_request(
        self,
        method: str,
        path: str,
        query: Dict,
        body: Dict,
    ) -> Dict:
        for route_path, handlers in self._routes.items():
            params = self._match_route(route_path, path)
            if params is not None:
                handler = handlers.get(method.upper())
                if handler:
                    try:
                        return handler(params, query, body)
                    except Exception as e:
                        logger.exception(f"API handler error: {e}")
                        return {
                            "status": 500,
                            "body": {"error": str(e)},
                        }
                return {
                    "status": 405,
                    "body": {"error": "Method not allowed"},
                }
        return {"status": 404, "body": {"error": "Not found"}}

    @staticmethod
    def _match_route(route: str, path: str) -> Optional[Dict[str, str]]:
        route_parts = route.split("/")
        path_parts = path.split("/")
        if len(route_parts) != len(path_parts):
            return None
        params = {}
        for r, p in zip(route_parts, path_parts):
            if r.startswith("{") and r.endswith("}"):
                params[r[1:-1]] = p
            elif r != p:
                return None
        return params if params else {}

    @staticmethod
    def _send_response(conn: socket.socket, response: Dict) -> None:
        status_code = response.get("status", 200)
        body = json.dumps(response.get("body", {}))
        status_text = {
            200: "OK",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
            405: "Method Not Allowed",
            500: "Internal Server Error",
        }.get(status_code, "Unknown")

        resp = (
            f"HTTP/1.1 {status_code} {status_text}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"Access-Control-Allow-Origin: *\r\n"
            f"Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\r\n"
            f"Access-Control-Allow-Headers: Content-Type, Authorization\r\n"
            f"Connection: close\r\n"
            f"\r\n"
            f"{body}"
        )
        try:
            conn.sendall(resp.encode())
        except Exception:
            pass

    def _check_auth(self, body: Dict) -> bool:
        if not self._secret:
            return True
        return body.get("secret") == self._secret

    def _handle_status(self, params: Dict, query: Dict, body: Dict) -> Dict:
        return {
            "status": 200,
            "body": {
                "name": "Purple Team C2",
                "version": "2.0.0",
                "api_version": "v1",
                "uptime": "N/A",
                "agents": c2_server.get_stats(),
            },
        }

    def _handle_list_agents(self, params: Dict, query: Dict, body: Dict) -> Dict:
        status = query.get("status", [None])[0]
        agents = c2_server.list_agents(status)
        return {"status": 200, "body": {"agents": agents, "count": len(agents)}}

    def _handle_get_agent(self, params: Dict, query: Dict, body: Dict) -> Dict:
        agent = c2_server.get_agent(params["id"])
        if agent:
            return {"status": 200, "body": agent}
        return {"status": 404, "body": {"error": "Agent not found"}}

    def _handle_send_command(self, params: Dict, query: Dict, body: Dict) -> Dict:
        if not self._check_auth(body):
            return {"status": 401, "body": {"error": "Unauthorized"}}
        command = body.get("command", "")
        if not command:
            return {"status": 400, "body": {"error": "No command specified"}}
        success = c2_server.send_command(params["id"], command)
        if success:
            return {"status": 200, "body": {"status": "sent", "command": command}}
        return {"status": 404, "body": {"error": "Agent not found"}}

    def _handle_disconnect(self, params: Dict, query: Dict, body: Dict) -> Dict:
        if not self._check_auth(body):
            return {"status": 401, "body": {"error": "Unauthorized"}}
        success = c2_server.disconnect_agent(params["id"])
        if success:
            return {"status": 200, "body": {"status": "disconnected"}}
        return {"status": 404, "body": {"error": "Agent not found"}}

    def _handle_get_output(self, params: Dict, query: Dict, body: Dict) -> Dict:
        clear = query.get("clear", ["true"])[0].lower() == "true"
        output = c2_server.get_cmd_buffer(params["id"], clear=clear)
        return {"status": 200, "body": {"output": output}}

    def _handle_list_alerts(self, params: Dict, query: Dict, body: Dict) -> Dict:
        limit = int(query.get("limit", ["50"])[0])
        severity = query.get("severity", [None])[0]
        alerts = db.list_alerts(limit=limit, severity=severity)
        return {"status": 200, "body": {"alerts": alerts, "count": len(alerts)}}

    def _handle_list_flows(self, params: Dict, query: Dict, body: Dict) -> Dict:
        limit = int(query.get("limit", ["100"])[0])
        ip = query.get("ip", [None])[0]
        flows = db.get_flows(limit=limit, src_ip=ip)
        return {"status": 200, "body": {"flows": flows, "count": len(flows)}}

    def _handle_list_scans(self, params: Dict, query: Dict, body: Dict) -> Dict:
        target = query.get("target", [None])[0]
        results = db.get_scan_results(target=target)
        return {"status": 200, "body": {"scans": results, "count": len(results)}}

    def _handle_stats(self, params: Dict, query: Dict, body: Dict) -> Dict:
        stats = c2_server.get_stats()
        return {"status": 200, "body": stats}

    def _handle_scan(self, params: Dict, query: Dict, body: Dict) -> Dict:
        if not self._check_auth(body):
            return {"status": 401, "body": {"error": "Unauthorized"}}
        target = body.get("target", "")
        ports = body.get("ports", "1-1024")
        if not target:
            return {"status": 400, "body": {"error": "No target specified"}}
        from ..agent.scanner import Scanner
        scanner = Scanner()
        results = scanner.scan(target, ports)
        return {"status": 200, "body": {"target": target, "results": results}}


api = RESTAPI()
