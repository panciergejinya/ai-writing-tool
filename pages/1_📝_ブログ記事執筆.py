import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

from utils.gemini_client import generate_text
from utils.prompts import build_blog_prompt

st.set_page_config(page_title="ブログ記事執筆", page_icon="📝")
st.title("📝 ブログ記事執筆AI")

topic = st.text_input("テーマ/キーワード", placeholder="例: 猫の飼い方")
length = st.selectbox("文字数目安", ["短め(約600字)", "標準(約1200字)", "長め(約2000字)"])
tone = st.selectbox("トーン", ["フォーマル", "カジュアル", "専門的"])

if st.button("生成", type="primary"):
    if not topic.strip():
        st.warning("テーマ/キーワードを入力してください。")
    else:
        with st.spinner("生成中..."):
            try:
                st.session_state.pop("blog_result", None)
                prompt = build_blog_prompt(topic=topic, length=length, tone=tone)
                result = generate_text(prompt)
                st.session_state["blog_result"] = result
            except RuntimeError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

if "blog_result" in st.session_state:
    st.markdown("### 生成結果")
    st.markdown(st.session_state["blog_result"])
    st.text_area("コピー用テキスト", st.session_state["blog_result"], height=300)
