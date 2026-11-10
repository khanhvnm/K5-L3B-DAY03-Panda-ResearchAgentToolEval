"""Run the whole lab pipeline against a real provider and fill artifacts/version_log.csv.

    python scripts/run_all.py --provider openrouter [--model openai/gpt-4o-mini] [--skip-group] [--skip-extension]

Steps (each one calls `run_eval.py`, which stores the evidence in runs/*.json):
  1. v0..v3 on the fixed base eval, each with its own artifacts/versions/<v>/ prompt + tools
     -> one row per version in artifacts/version_log.csv (metric = case_accuracy)
  2. v3 on data/eval_group.json (team cases)
  3. v3 on data/eval_research_extension.json (policy + arXiv)
  4. scripts/parse_runs.py -> analysis/*.csv

It needs real API keys in .env, so it is never run by pytest.
Careful: group case GM04 makes the model call `send(confirmed=true)`; leave TELEGRAM_BOT_TOKEN /
TELEGRAM_CHAT_ID out of .env if you do not want a real Telegram message.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

VERSIONS = [
    ("v0", "baseline", "Starter nguyên bản", "Đo hành vi chưa tối ưu: prompt xấu cố ý + mô tả tool mơ hồ"),
    ("v1", "system_prompt.md",
     "Bỏ chỉ dẫn xấu (đoán thay vì hỏi, gửi không cần xác nhận, ép một bước); thêm luật clarify / confirm-before-send",
     "Prompt xấu là nguyên nhân chính của missing_info + wrong_boundary; sửa prompt sẽ làm các case clarify/yes_no PASS"),
    ("v2", "tools.yaml",
     "Viết lại description mọi tool (USE WHEN / DO NOT USE) + convention args (handle không @, topic=news, timeframe, Top)",
     "Mô tả mơ hồ gây wrong_tool và wrong_arg_value; quy ước args rõ ràng sẽ sửa các case routing/args"),
    ("v3", "system_prompt.md + tools.yaml",
     "Bảng routing, ép clarify(response_type=yes_no) mọi yêu cầu gửi/đăng Telegram, luật multi-turn + parallel calls, khai báo 4 tool mới",
     "Tách rõ clarify(yes_no) cho hành động gửi bất kể đã có nội dung hay chưa sẽ sửa R12 lên 1.0; 4 tool mới không làm rớt routing cũ"),
]


def run_cmd(cmd: list[str]) -> str:
    print("$", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, encoding="utf-8")
    print(proc.stdout)
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(f"command failed with exit code {proc.returncode}")
    return proc.stdout


def run_eval(cmd: list[str]) -> str:
    stdout = run_cmd(cmd)
    match = re.search(r"Saved: (.+\.json)", stdout)
    if not match:
        raise SystemExit("run_eval did not report a saved run file")
    return match.group(1).strip()


def eval_cmd(args: argparse.Namespace, version: str, suite: str, cases: str, folder: str) -> list[str]:
    cmd = [PY, "run_eval.py", "--provider", args.provider, "--version", version, "--suite", suite,
           "--eval-cases", cases,
           "--system-prompt", f"artifacts/versions/{folder}/system_prompt.md",
           "--tools", f"artifacts/versions/{folder}/tools.yaml"]
    if args.model:
        cmd += ["--model", args.model]
    return cmd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="openrouter", choices=["openai", "openrouter", "anthropic", "gemini", "ollama"])
    parser.add_argument("--model", default=None)
    parser.add_argument("--skip-group", action="store_true")
    parser.add_argument("--skip-extension", action="store_true")
    args = parser.parse_args()

    for old_run in (ROOT / "runs").glob("v3_*.json"):
        old_run.unlink(missing_ok=True)

    log = ROOT / "artifacts" / "version_log.csv"
    logged_versions: set[str] = set()
    if log.exists():
        for line in log.read_text(encoding="utf-8").strip().splitlines()[1:]:
            if line.strip():
                logged_versions.add(line.split(",", 1)[0].strip())

    preflight_cmd = [PY, "scripts/preflight_provider.py", "--provider", args.provider]
    if args.model:
        preflight_cmd += ["--model", args.model]
    preflight = subprocess.run(preflight_cmd, cwd=ROOT, text=True, capture_output=True, encoding="utf-8")
    if preflight.returncode != 0:
        print(preflight.stderr, file=sys.stderr)
        raise SystemExit(f"preflight failed with exit code {preflight.returncode}")
    print(preflight.stdout)

    for version, changed, reason, hypothesis in VERSIONS:
        if version in logged_versions:
            print(f"Skipping {version} (already logged in version_log.csv)")
            continue
        run_file = run_eval(eval_cmd(args, version, "base", "data/eval_base.json", version))
        run_cmd([PY, "scripts/log_version.py", run_file, "--changed", changed, "--reason", reason, "--hypothesis", hypothesis])

    if not args.skip_group:
        run_eval(eval_cmd(args, "v3", "group", "data/eval_group.json", "v3"))
    if not args.skip_extension:
        run_eval(eval_cmd(args, "v3", "extension", "data/eval_research_extension.json", "v3"))

    (ROOT / "analysis").mkdir(exist_ok=True)
    run_parse = subprocess.run([PY, "scripts/parse_runs.py", "runs/", "--output", "analysis/all_runs.csv"], cwd=ROOT, text=True)
    print("parse_runs exit code:", run_parse.returncode)
    print("Done. Next: read runs/*.json, fill artifacts/REPORT.md Phần B (B1-B3), then python chat.py --version v3.")


if __name__ == "__main__":
    main()
