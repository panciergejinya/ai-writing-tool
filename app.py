import os

import streamlit as st
from dotenv import load_dotenv

st.set_page_config(page_title="AIライティングツール", page_icon="🖋️")

load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    st.error("GEMINI_API_KEY が未設定です。.env ファイルを作成してキーを設定してください。")

st.title("🖋️ AIライティングツール")
st.write(
    "個人用のAIライティング支援ツールです。左側のサイドバーから使いたい機能を選んでください。"
)

st.markdown(
    """
### 利用できる機能
- 📝 **ブログ記事執筆**: テーマを入力するとブログ記事の下書きを生成します
- ✉️ **メール返信**: 受信メールに対する返信文を作成します
- 📄 **要約**: 長い文章を要約します
- 🌐 **翻訳**: 日本語⇔英語の翻訳を行います

### 事前準備
`.env` ファイルに `GEMINI_API_KEY` を設定してから起動してください。
"""
)
