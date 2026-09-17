import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

from utils.gemini_client import generate_text
from utils.prompts import build_email_reply_prompt

st.set_page_config(page_title="メール返信", page_icon="✉️")
st.title("✉️ メール返信AI")

original_email = st.text_area(
    "受信メール本文", height=200, placeholder="返信したいメールの本文を貼り付けてください"
)
direction = st.selectbox("返信の方向性", ["承諾", "辞退", "質問する", "お礼", "その他自由記述"])
tone = st.selectbox("口調", ["丁寧", "ビジネスカジュアル"])

if st.button("生成", type="primary"):
    if not original_email.strip():
        st.warning("受信メール本文を入力してください。")
    else:
        with st.spinner("生成中..."):
            try:
                prompt = build_email_reply_prompt(
                    original_email=original_email, direction=direction, tone=tone
                )
                result = generate_text(prompt)
                st.session_state["email_result"] = result
            except RuntimeError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

if "email_result" in st.session_state:
    st.markdown("### 生成結果")
    st.text_area("返信文案", st.session_state["email_result"], height=300)
