import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..core.config import config
from ..core.logger import logger


class WAFManager:
    def __init__(self):
        self._api_token = config.get("waf.cloudflare_api_key", "")
        self._email = config.get("waf.cloudflare_email", "")
        self._base_url = "https://api.cloudflare.com/client/v4"
        self._zones: Dict[str, str] = {}
        self._rulesets: Dict[str, list] = {}

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._api_token:
            headers["Authorization"] = f"Bearer {self._api_token}"
        elif self._email:
            headers["X-Auth-Email"] = self._email
            headers["X-Auth-Key"] = self._api_token
        return headers

    def _request(self, method: str, path: str, data: Optional[Dict] = None) -> Optional[Dict]:
        import requests as req
        try:
            url = f"{self._base_url}{path}"
            if method == "GET":
                r = req.get(url, headers=self._headers(), timeout=15)
            elif method == "POST":
                r = req.post(url, headers=self._headers(), json=data, timeout=15)
            elif method == "PUT":
                r = req.put(url, headers=self._headers(), json=data, timeout=15)
            elif method == "DELETE":
                r = req.delete(url, headers=self._headers(), timeout=15)
            else:
                return None
            return r.json()
        except Exception as e:
            logger.error(f"WAF request failed: {e}")
            return None

    def list_zones(self) -> List[Dict[str, Any]]:
        result = self._request("GET", "/zones")
        if result and result.get("success"):
            zones = result.get("result", [])
            self._zones = {z["name"]: z["id"] for z in zones}
            return zones
        return []

    def get_zone_id(self, domain: str) -> Optional[str]:
        if domain in self._zones:
            return self._zones[domain]
        zones = self.list_zones()
        for z in zones:
            if z["name"] == domain:
                return z["id"]
        return None

    def list_rulesets(self, domain: str) -> List[Dict[str, Any]]:
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            logger.error(f"Zone not found for {domain}")
            return []
        result = self._request("GET", f"/zones/{zone_id}/rulesets")
        if result and result.get("success"):
            self._rulesets[domain] = result.get("result", [])
            return self._rulesets[domain]
        return []

    def create_waf_rule(
        self,
        domain: str,
        ip: str,
        action: str = "block",
        notes: str = "",
    ) -> Optional[Dict]:
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            return None

        payload = {
            "name": f"Purple Team - Block {ip}",
            "description": notes or f"Block rule for {ip}",
            "action": action,
            "expression": f"(ip.src eq {ip})",
        }
        return self._request("POST", f"/zones/{zone_id}/rulesets/entrypoint/rules", payload)

    def block_ip(self, domain: str, ip: str, notes: str = "") -> Optional[Dict]:
        return self.create_waf_rule(domain, ip, "block", notes)

    def challenge_ip(self, domain: str, ip: str) -> Optional[Dict]:
        return self.create_waf_rule(domain, ip, "challenge", "CAPTCHA challenge")

    def allow_ip(self, domain: str, ip: str) -> Optional[Dict]:
        return self.create_waf_rule(domain, ip, "allow", "IP whitelist")

    def delete_rule(self, domain: str, rule_id: str) -> bool:
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            return False
        result = self._request("DELETE", f"/zones/{zone_id}/rulesets/entrypoint/rules/{rule_id}")
        return bool(result and result.get("success"))

    def list_rules(self, domain: str) -> List[Dict[str, Any]]:
        rulesets = self.list_rulesets(domain)
        rules = []
        for rs in rulesets:
            for rule in rs.get("rules", []):
                rules.append(rule)
        return rules

    def get_security_events(
        self, domain: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            return []
        result = self._request(
            "GET",
            f"/zones/{zone_id}/security/events?per_page={limit}",
        )
        if result and result.get("success"):
            return result.get("result", [])
        return []

    def analyze_threat(self, ip: str) -> Dict[str, Any]:
        threat_info = {
            "ip": ip,
            "reputation": "unknown",
            "categories": [],
            "reports": [],
        }
        try:
            result = self._request("GET", f"/v4/ip/{ip}")
            if result:
                threat_info["reputation"] = "malicious" if result.get("data", {}).get("threat_score", 0) > 50 else "clean"
        except Exception:
            pass
        return threat_info

    def generate_report(self, domain: str) -> Dict[str, Any]:
        rules = self.list_rules(domain)
        events = self.get_security_events(domain)
        return {
            "domain": domain,
            "total_rules": len(rules),
            "total_events": len(events),
            "rules": rules[:20],
            "events": events[:20],
            "generated_at": __import__("datetime").datetime.utcnow().isoformat(),
        }


class IPReputation:
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        self._api_keys = {
            "virustotal": config.get("waf.virustotal_key", ""),
            "abuseipdb": config.get("waf.abuseipdb_key", ""),
        }

    def check_ip(self, ip: str) -> Dict[str, Any]:
        if ip in self._cache:
            return self._cache[ip]

        result = {"ip": ip, "sources": {}}

        if self._api_keys.get("virustotal"):
            result["sources"]["virustotal"] = self._check_virustotal(ip)
        if self._api_keys.get("abuseipdb"):
            result["sources"]["abuseipdb"] = self._check_abuseipdb(ip)

        try:
            result["geo"] = self._geo_lookup(ip)
        except Exception:
            result["geo"] = {}

        mal_count = sum(
            1 for s in result["sources"].values() if s.get("malicious", False)
        )
        result["malicious"] = mal_count > 0
        result["score"] = min(100, mal_count * 50)

        self._cache[ip] = result
        return result

    def _check_virustotal(self, ip: str) -> Dict[str, bool]:
        import requests
        try:
            r = requests.get(
                f"https://www.virustotal.com/api/v3/ip_addresses/{ip}",
                headers={"x-apikey": self._api_keys["virustotal"]},
                timeout=10,
            )
            if r.status_code == 200:
                data = r.json()
                stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                return {"malicious": stats.get("malicious", 0) > 0, "details": stats}
        except Exception:
            pass
        return {"malicious": False, "details": {}}

    def _check_abuseipdb(self, ip: str) -> Dict[str, Any]:
        import requests
        try:
            r = requests.get(
                "https://api.abuseipdb.com/api/v2/check",
                headers={"Key": self._api_keys["abuseipdb"], "Accept": "application/json"},
                params={"ipAddress": ip, "maxAgeInDays": "90"},
                timeout=10,
            )
            if r.status_code == 200:
                data = r.json().get("data", {})
                return {
                    "malicious": data.get("abuseConfidenceScore", 0) > 50,
                    "score": data.get("abuseConfidenceScore", 0),
                    "country": data.get("countryCode", ""),
                }
        except Exception:
            pass
        return {"malicious": False, "score": 0}

    @staticmethod
    def _geo_lookup(ip: str) -> Dict[str, str]:
        import requests
        try:
            r = requests.get(f"http://ip-api.com/json/{ip}?fields=country,regionName,city,isp,org,as", timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return {}


waf_manager = WAFManager()
ip_reputation = IPReputation()
