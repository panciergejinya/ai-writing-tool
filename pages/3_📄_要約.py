import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

from utils.gemini_client import generate_text
from utils.prompts import build_summary_prompt

st.set_page_config(page_title="要約", page_icon="📄")
st.title("📄 要約AI")

text = st.text_area("要約したい本文", height=250, placeholder="要約したい文章を貼り付けてください")
length = st.selectbox("要約の長さ", ["一言", "3行", "詳細"])

if st.button("生成", type="primary"):
    if not text.strip():
        st.warning("要約したい本文を入力してください。")
    else:
        with st.spinner("生成中..."):
            try:
                st.session_state.pop("summary_result", None)
                prompt = build_summary_prompt(text=text, length=length)
                result = generate_text(prompt)
                st.session_state["summary_result"] = result
            except RuntimeError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

if "summary_result" in st.session_state:
    st.markdown("### 要約結果")
    st.markdown(st.session_state["summary_result"])
