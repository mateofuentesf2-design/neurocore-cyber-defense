import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional

EVENT_STORE_PATH = "/tmp/neurocore_events.json"

class CorrelationEngine:
    def __init__(self, window_seconds=300, threshold=5):
        self.window_seconds = window_seconds
        self.threshold = threshold
        self.event_buffer: List[Dict] = []
        self.ip_counts: Dict[str, int] = defaultdict(int)
        self.ip_times: Dict[str, List[float]] = defaultdict(list)
        self.failed_logins: Dict[str, List[float]] = defaultdict(list)
        self.port_scans: Dict[str, set] = defaultdict(set)
        self._load_events()

    def _load_events(self):
        import json
        if os.path.exists(EVENT_STORE_PATH):
            try:
                with open(EVENT_STORE_PATH, "r") as f:
                    data = json.load(f)
                    self.event_buffer = data.get("events", [])[-1000:]
            except:
                pass

    def _save_events(self):
        import json
        with open(EVENT_STORE_PATH, "w") as f:
            json.dump({"events": self.event_buffer[-1000:]}, f)

    def correlate(self, event: Dict) -> List[str]:
        alerts = []
        raw = event.get("raw", "").lower()
        ip = event.get("ip")
        source = event.get("source", "")
        timestamp = time.time()

        self.event_buffer.append({**event, "timestamp": timestamp})
        self._save_events()

        if ip:
            if self._check_brute_force(ip, timestamp):
                alerts.append("brute_force_correlated")
            if self._check_port_scan(ip, raw, timestamp):
                alerts.append("port_scan_correlated")
            if self._check_ddos(ip, timestamp):
                alerts.append("ddos_correlated")
            if self._check_credential_stuffing(ip, raw, timestamp):
                alerts.append("credential_stuffing")

        if self._check_slowloris(source, timestamp):
            alerts.append("slowloris_attack")

        if self._check_data_exfiltration(ip, timestamp):
            alerts.append("data_exfiltration_correlated")

        return alerts

    def _check_brute_force(self, ip: str, timestamp: float) -> bool:
        window = timestamp - self.window_seconds
        self.failed_logins[ip] = [
            t for t in self.failed_logins[ip] if t > window
        ]
        if "failed" in str(self.event_buffer[-1].get("raw", "")).lower():
            self.failed_logins[ip].append(timestamp)
        
        if len(self.failed_logins[ip]) >= self.threshold:
            self.failed_logins[ip] = []
            return True
        return False

    def _check_port_scan(self, ip: str, raw: str, timestamp: float) -> bool:
        window = timestamp - self.window_seconds
        self.port_scans[ip] = self.port_scans[ip].copy()
        
        port_match = self._extract_port(raw)
        if port_match:
            self.port_scans[ip].add(port_match)
            if len(self.port_scans[ip]) >= 10:
                self.port_scans[ip] = set()
                return True
        return False

    def _extract_port(self, raw: str) -> Optional[int]:
        import re
        match = re.search(r":(\d{2,5})\b", raw)
        if match:
            port = int(match.group(1))
            if 1 <= port <= 65535:
                return port
        return None

    def _check_ddos(self, ip: str, timestamp: float) -> bool:
        window = timestamp - self.window_seconds
        self.ip_times[ip] = [t for t in self.ip_times[ip] if t > window]
        self.ip_times[ip].append(timestamp)
        
        if len(self.ip_times[ip]) >= 50:
            self.ip_times[ip] = []
            return True
        return False

    def _check_credential_stuffing(self, ip: str, raw: str, timestamp: float) -> bool:
        if "login" in raw and "failed" in raw:
            return False
        return False

    def _check_slowloris(self, source: str, timestamp: float) -> bool:
        recent = [e for e in self.event_buffer[-30:] if e.get("source") == source]
        if len(recent) >= 25:
            return True
        return False

    def _check_data_exfiltration(self, ip: str, timestamp: float) -> bool:
        if not ip:
            return False
        window = timestamp - 60
        recent = [
            e for e in self.event_buffer[-100:]
            if e.get("ip") == ip and e.get("timestamp", 0) > window
        ]
        total_size = sum(e.get("bytes_sent", 0) for e in recent)
        if total_size > 10000000:
            return True
        return False

    def get_correlation_stats(self) -> Dict:
        return {
            "unique_ips": len(self.ip_counts),
            "brute_force_targets": len(self.failed_logins),
            "port_scan_ips": len(self.port_scans),
            "buffer_size": len(self.event_buffer),
        }


engine = CorrelationEngine()
correlate = engine.correlate