import json
import socket
import time
from pathlib import Path

import psutil
import requests

CONFIG_PATH = Path(__file__).with_name("agent_config.json")

def collect_processes():
    # Prime CPU calculation to avoid zeros
    for p in psutil.process_iter():
        try:
            p.cpu_percent(None)
        except Exception:
            pass
    time.sleep(0.2)

    procs = []
    for p in psutil.process_iter(attrs=["pid", "ppid", "name", "cmdline"]):
        try:
            info = p.info
            cpu = p.cpu_percent(None)
            mem = p.memory_info().rss if p.is_running() else None
            procs.append({
                "pid": int(info.get("pid", 0)),
                "ppid": int(info.get("ppid", 0)),
                "name": info.get("name") or "",
                "cpu_percent": float(cpu) if cpu is not None else None,
                "mem_rss": int(mem) if mem is not None else None,
                "cmdline": " ".join(info.get("cmdline") or [])[:8000],
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        except Exception:
            continue
    return procs

def main():
    cfg = json.loads(CONFIG_PATH.read_text())
    endpoint = cfg["endpoint"]
    api_key = cfg["api_key"]
    hostname = socket.gethostname()

    payload = {
        "hostname": hostname,
        "processes": collect_processes(),
    }

    try:
        r = requests.post(endpoint, json=payload, headers={"X-API-Key": api_key}, timeout=10)
        r.raise_for_status()
        print("Sent snapshot:", r.json())
    except Exception as e:
        print("Failed to send snapshot:", e)

if __name__ == "__main__":
    main()
