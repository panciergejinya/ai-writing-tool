import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

from utils.gemini_client import generate_text
from utils.prompts import build_translation_prompt

st.set_page_config(page_title="翻訳", page_icon="🌐")
st.title("🌐 翻訳AI")

text = st.text_area("原文", height=200, placeholder="翻訳したい文章を貼り付けてください")
direction = st.selectbox("翻訳方向", ["日→英", "英→日"])
tone = st.selectbox("トーン", ["自然", "フォーマル"])

if st.button("生成", type="primary"):
    if not text.strip():
        st.warning("原文を入力してください。")
    else:
        with st.spinner("翻訳中..."):
            try:
                st.session_state.pop("translation_result", None)
                prompt = build_translation_prompt(text=text, direction=direction, tone=tone)
                result = generate_text(prompt)
                st.session_state["translation_result"] = result
            except RuntimeError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

if "translation_result" in st.session_state:
    st.markdown("### 翻訳結果")
    st.text_area("翻訳文", st.session_state["translation_result"], height=250)
