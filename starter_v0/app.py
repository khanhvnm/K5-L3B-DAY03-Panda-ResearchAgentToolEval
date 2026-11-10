"""Streamlit UI for the Research Agent.

Run:   streamlit run app.py
Share: cloudflared tunnel --url http://localhost:8501   (see README, "Deploy nhanh")

The UI reuses the exact same tool loop as `chat.py` (`run_model_tool_loop`), so behaviour matches the
eval/transcripts. Every conversation is also written to `transcripts/*.transcript.json`.
"""
from __future__ import annotations

import importlib
import json
from datetime import datetime
from pathlib import Path

import streamlit as st

import chat as chat_core
import tools.fetch.tool as _fetch_mod
import tools.lookup.tool as _lookup_mod
import tools.social_search.tool as _social_mod
import tools.timeline.tool as _timeline_mod
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

# Hot-reload updated tool implementations into TOOL_FUNCTIONS in-place so live Streamlit reruns pick up edits immediately
TOOL_FUNCTIONS["lookup"] = importlib.reload(_lookup_mod).web_search
TOOL_FUNCTIONS["timeline"] = importlib.reload(_timeline_mod).get_user_tweets
TOOL_FUNCTIONS["social_search"] = importlib.reload(_social_mod).search_tweets
TOOL_FUNCTIONS["fetch"] = importlib.reload(_fetch_mod).read_url

ROOT = Path(__file__).parent
ARTIFACTS = ROOT / "artifacts"
TRANSCRIPTS = ROOT / "transcripts"

EXAMPLES = [
    "Tin tức AI hôm nay có gì nổi bật?",
    "Lấy 5 tweet mới nhất của Sam Altman",
    "Mọi người đang bàn gì về GPT-5 trên Twitter?",
    "Repo GitHub nào hay về RAG, nhiều sao nhất?",
    "Trên Hacker News người ta bàn gì về LLM agents?",
    "Cho mình tóm tắt Wikipedia về Alan Turing",
    "Theo policy công ty, tweet viral có được coi là fact không?",
    "Tìm paper arXiv về AI agent evaluation",
    "Hôm nay là thứ mấy?",
]

st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")


@st.cache_resource(show_spinner=False)
def get_provider(name: str):
    return make_provider(name)


def available_versions() -> dict[str, tuple[Path, Path]]:
    versions = {"final (artifacts/)": (ARTIFACTS / "system_prompt.md", ARTIFACTS / "tools.yaml")}
    for folder in sorted((ARTIFACTS / "versions").glob("v*")):
        prompt, tools = folder / "system_prompt.md", folder / "tools.yaml"
        if prompt.exists() and tools.exists():
            versions[folder.name] = (prompt, tools)
    return versions


def save_transcript() -> Path:
    meta = st.session_state.meta
    path = TRANSCRIPTS / f"{meta['transcript_id']}.transcript.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    meta["updated_at"] = datetime.now().isoformat(timespec="seconds")
    path.write_text(json.dumps({**meta, "turns": st.session_state.turns}, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path


def reset_conversation() -> None:
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.turns = []
    st.session_state.pop("meta", None)


for key, default in (("messages", []), ("history", []), ("turns", [])):
    st.session_state.setdefault(key, default)

TOOL_DESCRIPTIONS_VI = {
    "clarify": "Hỏi lại người dùng khi thiếu thông tin bắt buộc hoặc cần xin xác nhận trước khi gửi tin.",
    "timeline": "Lấy các bài đăng mới nhất của một tài khoản X/Twitter cụ thể.",
    "social_search": "Tìm kiếm thảo luận mạng xã hội theo chủ đề/từ khóa (phổ biến nhất hoặc mới nhất).",
    "lookup": "Tìm kiếm tin tức và bài viết trên web theo khoảng thời gian (ngày, tuần, tháng, năm).",
    "fetch": "Đọc và trích xuất nội dung chi tiết từ một đường dẫn URL cụ thể.",
    "format": "Trình bày danh sách thông tin đã thu thập thành bản tin Markdown hoàn chỉnh.",
    "send": "Gửi bản tin lên kênh Telegram (chỉ gửi sau khi người dùng đã xác nhận đồng ý).",
    "policy": "Tra cứu quy định & chính sách nội bộ của công ty (trích nguồn, truyền thông, bảo mật).",
    "papers": "Tìm kiếm bài báo khoa học trên arXiv theo chủ đề nghiên cứu.",
    "paper_text": "Tải và trích xuất nội dung văn bản từ bài báo PDF trên arXiv theo mã bài.",
    "hackernews": "Tìm kiếm tin công nghệ và thảo luận của lập trình viên trên Hacker News.",
    "github_search": "Tìm kiếm kho mã nguồn mở (repository) trên GitHub theo số sao hoặc ngày cập nhật.",
    "wikipedia": "Tra cứu kiến thức nền tảng, định nghĩa khái niệm và tiểu sử trên Wikipedia (Việt/Anh).",
    "current_time": "Xem ngày, giờ và thứ hiện tại theo múi giờ (mặc định UTC+7 Việt Nam).",
}

# Cấu hình mặc định tối ưu (cố định để người dùng thử không bấm nhầm làm lỗi cấu hình)
provider_name = "gemini"
model = ""
version_label = "v3"
prompt_path = ARTIFACTS / "system_prompt.md"
tools_path = ARTIFACTS / "tools.yaml"
history_window = 5
max_rounds = 4
declarations = load_tool_declarations(tools_path)

# ----------------------------- sidebar -----------------------------
with st.sidebar:
    st.title("🔎 Research Agent")
    if st.button("🗑️ Cuộc trò chuyện mới", use_container_width=True):
        reset_conversation()
        st.rerun()

    st.markdown("**💡 Câu hỏi gợi ý (Bấm để thử):**")
    for index, example in enumerate(EXAMPLES):
        if st.button(example, key=f"ex{index}", use_container_width=True):
            st.session_state.queued = example

    with st.expander(f"🧰 Danh sách {len(declarations)} công cụ (Tools)", expanded=True):
        for item in declarations:
            name = item["name"]
            desc_vi = TOOL_DESCRIPTIONS_VI.get(name, item.get("description", ""))
            st.caption(f"`{name}` — {desc_vi}")

# ----------------------------- main chat -----------------------------
st.header("Research Agent")
st.caption("Web news · X/Twitter · đọc URL · arXiv · policy nội bộ · GitHub · Hacker News · Wikipedia · gửi Telegram (có xác nhận)")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        for event in message.get("events", []):
            with st.expander(f"🔧 {event['tool']}({json.dumps(event.get('args', {}), ensure_ascii=False)})"):
                st.json(event.get("result", {}), expanded=False)

user_text = st.chat_input("Hỏi agent...") or st.session_state.pop("queued", None)

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        try:
            provider = get_provider(provider_name)
            artifact_version = build_artifact_version(version_label.split(" ")[0], prompt_path, tools_path)
            if "meta" not in st.session_state:
                st.session_state.meta = {
                    "transcript_id": f"ui_{artifact_version.version}_{provider_name}_{datetime.now().strftime('%Y%m%dT%H%M%S%f')}",
                    **artifact_version_dict(artifact_version),
                    "provider": provider_name,
                    "model": model or getattr(provider, "default_model", None),
                    "system_prompt": str(prompt_path),
                    "tools": str(tools_path),
                    "history_window": history_window,
                    "max_tool_rounds": max_rounds,
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                }
            messages = [
                {"role": "system", "content": prompt_path.read_text(encoding="utf-8")},
                *chat_core.trim_history(st.session_state.history, history_window),
                {"role": "user", "content": user_text},
            ]
            with st.spinner("Agent đang suy nghĩ và gọi tool..."):
                result = chat_core.run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=to_openai_tools(declarations),
                    model=model or None,
                    max_tool_rounds=max_rounds,
                )
            answer = result["assistant_text"]
            events = result["tool_events"]
            st.markdown(answer)
            if result["status"] == "waiting_for_user":
                st.info("Agent đang chờ bạn trả lời câu hỏi ở trên.")
            for event in events:
                with st.expander(f"🔧 {event['tool']}({json.dumps(event.get('args', {}), ensure_ascii=False)})"):
                    st.json(event.get("result", {}), expanded=False)
            st.session_state.messages.append({"role": "assistant", "content": answer, "events": events})
            st.session_state.history += [{"role": "user", "content": user_text}, {"role": "assistant", "content": answer}]
            st.session_state.turns.append({"turn_index": len(st.session_state.turns) + 1, "user": user_text, **result})
            save_transcript()
        except Exception as exc:  # show provider/key errors in the UI instead of crashing
            st.error(f"{type(exc).__name__}: {exc}")
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {type(exc).__name__}: {exc}"})
