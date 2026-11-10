"""Start Streamlit (port 8501) + Cloudflare Tunnel and write the public URL into artifacts/REPORT.md.

Usage:
    .venv\\Scripts\\python.exe scripts/serve_tunnel.py
"""
from __future__ import annotations

import re
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = Path(sys.executable)
CLOUDFLARED = PY.parent / "cloudflared.exe"
REPORT = ROOT / "artifacts" / "REPORT.md"


def update_report_url(url: str) -> None:
    if not REPORT.exists():
        return
    text = REPORT.read_text(encoding="utf-8")
    updated = re.sub(
        r"^>\s*URL:.*$",
        f"> URL: {url} (local: `http://localhost:8501`)",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if updated != text:
        REPORT.write_text(updated, encoding="utf-8")


def is_port_open(port: int = 8501) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def main() -> int:
    if not CLOUDFLARED.exists():
        raise SystemExit(f"cloudflared binary not found at {CLOUDFLARED}")
    socket.gethostbyname("api.trycloudflare.com")

    st_proc: subprocess.Popen[str] | None = None
    if is_port_open(8501):
        print("Streamlit is already running on http://localhost:8501", flush=True)
    else:
        streamlit_cmd = [
            str(PY), "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.headless", "true",
        ]
        print("Starting Streamlit on http://localhost:8501 ...", flush=True)
        st_proc = subprocess.Popen(
            streamlit_cmd,
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        for _ in range(20):
            if is_port_open(8501):
                break
            time.sleep(0.5)

    tunnel_cmd = [
        str(CLOUDFLARED),
        "tunnel",
        "--url",
        "http://localhost:8501",
        "--protocol",
        "http2",
        "--no-autoupdate",
    ]
    print("Starting Cloudflare Tunnel ...", flush=True)
    cf_proc = subprocess.Popen(
        tunnel_cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    url_pattern = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")
    public_url: str | None = None
    try:
        assert cf_proc.stdout is not None
        for line in cf_proc.stdout:
            print(line, end="", flush=True)
            if not public_url:
                match = url_pattern.search(line)
                if match:
                    public_url = match.group(0)
                    update_report_url(public_url)
                    print(f"\n=== PUBLIC TUNNEL READY: {public_url} ===\n", flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        cf_proc.terminate()
        if st_proc is not None:
            st_proc.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
