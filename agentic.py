"""Small, deterministic agent layer for lead import and sequential call orchestration."""
import csv
import os
import threading
import time
from datetime import datetime


class LeadOperationsAgent:
    def __init__(self, csv_path, call_lead):
        self.csv_path = csv_path
        self.call_lead = call_lead
        self._lock = threading.Lock()
        self.queue = []
        self.running = False
        self.completed = 0
        self.last_error = ""
        self.stop_requested = False

    def import_csv(self, file_object):
        rows = list(csv.DictReader(file_object.stream.read().decode("utf-8-sig").splitlines()))
        leads = []
        for row in rows:
            name = (row.get("name") or row.get("customer_name") or row.get("student_name") or "").strip()
            phone = (row.get("phone") or row.get("mobile") or row.get("mobile_number") or row.get("student_phone") or "").strip()
            age = (row.get("age") or "").strip()
            language = (row.get("language") or row.get("preferred_language") or "en-IN").strip()
            if name and phone:
                leads.append({"name": name, "age": age, "phone": phone, "language": language, "status": "queued"})
        with self._lock:
            self.queue = leads
            self.completed = 0
            self.last_error = ""
        return leads

    def snapshot(self):
        with self._lock:
            return {"queued": len(self.queue), "completed": self.completed, "running": self.running, "last_error": self.last_error}

    def start(self):
        with self._lock:
            if self.running or not self.queue:
                return False
            self.running = True
            self.stop_requested = False
        threading.Thread(target=self._run, daemon=True).start()
        return True

    def _run(self):
        while True:
            with self._lock:
                if self.stop_requested or not self.queue:
                    self.running = False
                    return
                lead = self.queue.pop(0)
            try:
                self.call_lead(lead)
            except Exception as exc:
                with self._lock:
                    self.last_error = str(exc)
            finally:
                with self._lock:
                    self.completed += 1
            time.sleep(1)

    def stop(self):
        with self._lock:
            self.stop_requested = True


def normalize_call_status(payload):
    return {
        "event": "call_completed",
        "call_sid": payload.get("CallSid", ""),
        "status": payload.get("CallStatus", "unknown"),
        "duration": payload.get("CallDuration", "0"),
    }
