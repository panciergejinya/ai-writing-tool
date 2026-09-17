# AIライティングツール Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ブログ記事執筆・メール返信・要約・翻訳の4機能を1つのStreamlitマルチページアプリにまとめた個人用AIライティングツールを構築する。

**Architecture:** Streamlitの`pages/`ディレクトリ規約でマルチページ化。Gemini API呼び出しは`utils/gemini_client.py`に、プロンプト組み立ては`utils/prompts.py`に共通化し、各ページはUI入力を集めてこれらを呼び出すだけにする。

**Tech Stack:** Python, Streamlit, google-genai(Gemini公式SDK), python-dotenv, pytest

## Global Constraints

- Gemini APIモデルは `gemini-2.5-flash` を使用する(設計書より)。
- APIキーは`.env`の`GEMINI_API_KEY`から`python-dotenv`で読み込む。DB・認証機能は実装しない。
- 生成履歴は保存しない。`st.session_state`での一時保持のみ(ページリロードで消える)。
- 要約AIの入力はテキスト貼り付けのみ対応(ファイルアップロード・URL取得は対象外)。
- 翻訳AIは日本語⇔英語のみ対応。
- `.env`は`.gitignore`で除外し、リポジトリには`.env.example`のみコミットする。

---

## Task 1: プロジェクト基盤の構築

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `README.md`
- Modify: `.gitignore`(既存ファイルの内容を確認し、不足があれば追記)

**Interfaces:**
- Produces: `requirements.txt`に列挙された依存パッケージ一式。以降の全タスクがこれに依存する。

- [ ] **Step 1: `requirements.txt` を作成する**

```text
streamlit
google-genai
python-dotenv
pytest
```

- [ ] **Step 2: `.env.example` を作成する**

```text
GEMINI_API_KEY=
```

- [ ] **Step 3: `.gitignore` の内容を確認し、以下が含まれていることを確認する(無ければ追記)**

```text
.env
__pycache__/
*.pyc
.venv/
venv/
```

- [ ] **Step 4: `README.md` を作成する**

```markdown
# AIライティングツール

個人用のAIライティング支援ツールです。Streamlit + Gemini APIで、ブログ記事執筆・メール返信文作成・要約・翻訳の4機能を提供します。

## セットアップ

1. 依存パッケージをインストール

   ```bash
   pip install -r requirements.txt
   ```

2. `.env.example` を `.env` にコピーし、`GEMINI_API_KEY` に取得したGemini APIキーを設定

   ```bash
   cp .env.example .env
   ```

3. アプリを起動

   ```bash
   streamlit run app.py
   ```

## 機能一覧

- 📝 ブログ記事執筆
- ✉️ メール返信
- 📄 要約
- 🌐 翻訳(日本語⇔英語)

## テスト

```bash
pytest
```
```

- [ ] **Step 5: 依存パッケージをインストールして動作確認**

Run: `pip install -r requirements.txt`
Expected: エラーなくインストールが完了する

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .env.example README.md .gitignore
git commit -m "chore: add project scaffolding (requirements, env example, README)"
```

---

## Task 2: Gemini API共通クライアント (`utils/gemini_client.py`)

**Files:**
- Create: `utils/__init__.py`
- Create: `utils/gemini_client.py`
- Test: `tests/test_gemini_client.py`
- Create: `tests/__init__.py`

**Interfaces:**
- Consumes: 環境変数 `GEMINI_API_KEY`(`.env`経由、Task 1で用意した`.env.example`が雛形)
- Produces: `generate_text(prompt: str) -> str`
  - `GEMINI_API_KEY`が未設定の場合、`RuntimeError`を送出する(メッセージに`"GEMINI_API_KEY"`を含む)
  - 正常時はGemini APIレスポンスの`.text`をそのまま返す
  - Task 5〜8の各ページはこの関数をそのまま呼び出す

- [ ] **Step 1: `utils/__init__.py` と `tests/__init__.py` を空ファイルとして作成する**

- [ ] **Step 2: 失敗するテストを書く**

`tests/test_gemini_client.py`:

```python
from unittest.mock import MagicMock, patch

import pytest

from utils.gemini_client import generate_text


def test_generate_text_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        generate_text("こんにちは")


def test_generate_text_returns_response_text(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    mock_response = MagicMock()
    mock_response.text = "生成されたテキスト"

    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_response

    with patch(
        "utils.gemini_client.genai.Client", return_value=mock_client_instance
    ) as mock_client_cls:
        result = generate_text("プロンプト")

    mock_client_cls.assert_called_once_with(api_key="dummy-key")
    mock_client_instance.models.generate_content.assert_called_once_with(
        model="gemini-2.5-flash",
        contents="プロンプト",
    )
    assert result == "生成されたテキスト"
```

- [ ] **Step 3: テストを実行して失敗することを確認する**

Run: `pytest tests/test_gemini_client.py -v`
Expected: FAIL(`utils.gemini_client` モジュールが存在しない、または `generate_text` が未定義のためImportError/ModuleNotFoundError)

- [ ] **Step 4: `utils/gemini_client.py` を実装する**

```python
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"


def generate_text(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY が設定されていません。.env ファイルに GEMINI_API_KEY を設定してください。"
        )
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return response.text
```

- [ ] **Step 5: テストを実行して成功することを確認する**

Run: `pytest tests/test_gemini_client.py -v`
Expected: PASS(2件とも成功)

- [ ] **Step 6: Commit**

```bash
git add utils/__init__.py utils/gemini_client.py tests/__init__.py tests/test_gemini_client.py
git commit -m "feat: add Gemini API client wrapper"
```

---

## Task 3: プロンプトテンプレート (`utils/prompts.py`)

**Files:**
- Create: `utils/prompts.py`
- Test: `tests/test_prompts.py`

**Interfaces:**
- Produces:
  - `build_blog_prompt(topic: str, length: str, tone: str) -> str`
  - `build_email_reply_prompt(original_email: str, direction: str, tone: str) -> str`
  - `build_summary_prompt(text: str, length: str) -> str`
  - `build_translation_prompt(text: str, direction: str, tone: str) -> str`
  - いずれもTask 5〜8の各ページが、UIで集めた値をそのまま渡して呼び出す

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_prompts.py`:

```python
from utils.prompts import (
    build_blog_prompt,
    build_email_reply_prompt,
    build_summary_prompt,
    build_translation_prompt,
)


def test_build_blog_prompt_includes_topic_length_tone():
    prompt = build_blog_prompt(topic="猫の飼い方", length="標準(約1200字)", tone="カジュアル")
    assert "猫の飼い方" in prompt
    assert "標準(約1200字)" in prompt
    assert "カジュアル" in prompt


def test_build_email_reply_prompt_includes_original_and_direction():
    prompt = build_email_reply_prompt(
        original_email="来週の会議に出席できますか?",
        direction="承諾",
        tone="丁寧",
    )
    assert "来週の会議に出席できますか?" in prompt
    assert "承諾" in prompt
    assert "丁寧" in prompt


def test_build_summary_prompt_includes_text_and_length():
    prompt = build_summary_prompt(text="長い本文がここに入ります。", length="3行")
    assert "長い本文がここに入ります。" in prompt
    assert "3行" in prompt


def test_build_translation_prompt_includes_text_direction_tone():
    prompt = build_translation_prompt(text="Hello, world!", direction="英→日", tone="自然")
    assert "Hello, world!" in prompt
    assert "英→日" in prompt
    assert "自然" in prompt
```

- [ ] **Step 2: テストを実行して失敗することを確認する**

Run: `pytest tests/test_prompts.py -v`
Expected: FAIL(`utils.prompts` モジュールが存在しないためImportError/ModuleNotFoundError)

- [ ] **Step 3: `utils/prompts.py` を実装する**

```python
def build_blog_prompt(topic: str, length: str, tone: str) -> str:
    return (
        "あなたはプロのブログライターです。以下の条件でブログ記事を書いてください。\n\n"
        f"テーマ: {topic}\n"
        f"文字数目安: {length}\n"
        f"トーン: {tone}\n\n"
        "出力形式:\n"
        "- 最初にタイトル案を1つ提示する\n"
        "- 続けて見出し(##)を使った本文を書く\n"
        "- Markdown形式で出力する"
    )


def build_email_reply_prompt(original_email: str, direction: str, tone: str) -> str:
    return (
        "あなたはビジネスメールの返信作成アシスタントです。"
        "以下の受信メールに対する返信文を作成してください。\n\n"
        f"受信メール本文:\n{original_email}\n\n"
        f"返信の方向性: {direction}\n"
        f"口調: {tone}\n\n"
        "出力形式:\n"
        "- 件名案を1行目に「件名: 」で始めて書く\n"
        "- 続けて本文を書く"
    )


def build_summary_prompt(text: str, length: str) -> str:
    return (
        "以下の文章を要約してください。\n\n"
        f"本文:\n{text}\n\n"
        f"要約の長さ: {length}\n"
    )


def build_translation_prompt(text: str, direction: str, tone: str) -> str:
    return (
        "以下の文章を翻訳してください。\n\n"
        f"原文:\n{text}\n\n"
        f"翻訳方向: {direction}\n"
        f"トーン: {tone}\n\n"
        "翻訳結果のみを出力してください。"
    )
```

- [ ] **Step 4: テストを実行して成功することを確認する**

Run: `pytest tests/test_prompts.py -v`
Expected: PASS(4件とも成功)

- [ ] **Step 5: Commit**

```bash
git add utils/prompts.py tests/test_prompts.py
git commit -m "feat: add prompt template builders"
```

---

## Task 4: ホーム画面 (`app.py`)

**Files:**
- Create: `app.py`

**Interfaces:**
- Consumes: なし(静的な説明画面)
- Produces: Streamlitアプリのエントリーポイント。`streamlit run app.py`で起動し、サイドバーにTask 5〜8の各ページへのリンクが自動表示される。

- [ ] **Step 1: `app.py` を実装する**

```python
import streamlit as st

st.set_page_config(page_title="AIライティングツール", page_icon="🖋️")

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
```

- [ ] **Step 2: 起動して表示を確認する**

Run: `streamlit run app.py`
Expected: ブラウザが開き、タイトルと機能一覧が表示される。この時点では`pages/`が空のためサイドバーにページリンクは出ない(Task 5以降で追加される)。確認後、ターミナルで`Ctrl+C`してサーバーを停止する。

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add home page"
```

---

## Task 5: ブログ記事執筆ページ

**Files:**
- Create: `pages/1_📝_ブログ記事執筆.py`

**Interfaces:**
- Consumes: `utils.gemini_client.generate_text(prompt: str) -> str`(Task 2)、`utils.prompts.build_blog_prompt(topic, length, tone) -> str`(Task 3)
- Produces: Streamlitページ。単体では他タスクから参照されない。

- [ ] **Step 1: `pages/1_📝_ブログ記事執筆.py` を実装する**

```python
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
```

- [ ] **Step 2: 起動して動作確認する**

Run: `streamlit run app.py`
Expected: サイドバーに「ブログ記事執筆」ページが表示される。テーマを空のまま「生成」を押すと警告が出る。テーマを入力し(`.env`にGEMINI_API_KEYが設定済みであること)「生成」を押すとスピナーの後に記事案が表示される。確認後、`Ctrl+C`でサーバーを停止する。

- [ ] **Step 3: Commit**

```bash
git add "pages/1_📝_ブログ記事執筆.py"
git commit -m "feat: add blog writing page"
```

---

## Task 6: メール返信ページ

**Files:**
- Create: `pages/2_✉️_メール返信.py`

**Interfaces:**
- Consumes: `utils.gemini_client.generate_text(prompt: str) -> str`(Task 2)、`utils.prompts.build_email_reply_prompt(original_email, direction, tone) -> str`(Task 3)
- Produces: Streamlitページ。単体では他タスクから参照されない。

- [ ] **Step 1: `pages/2_✉️_メール返信.py` を実装する**

```python
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
```

- [ ] **Step 2: 起動して動作確認する**

Run: `streamlit run app.py`
Expected: サイドバーに「メール返信」ページが表示される。受信メール本文を空のまま「生成」を押すと警告が出る。本文を入力して「生成」を押すと返信文案が表示される。確認後、`Ctrl+C`でサーバーを停止する。

- [ ] **Step 3: Commit**

```bash
git add "pages/2_✉️_メール返信.py"
git commit -m "feat: add email reply page"
```

---

## Task 7: 要約ページ

**Files:**
- Create: `pages/3_📄_要約.py`

**Interfaces:**
- Consumes: `utils.gemini_client.generate_text(prompt: str) -> str`(Task 2)、`utils.prompts.build_summary_prompt(text, length) -> str`(Task 3)
- Produces: Streamlitページ。単体では他タスクから参照されない。

- [ ] **Step 1: `pages/3_📄_要約.py` を実装する**

```python
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
```

- [ ] **Step 2: 起動して動作確認する**

Run: `streamlit run app.py`
Expected: サイドバーに「要約」ページが表示される。本文を空のまま「生成」を押すと警告が出る。本文を入力して「生成」を押すと要約結果が表示される。確認後、`Ctrl+C`でサーバーを停止する。

- [ ] **Step 3: Commit**

```bash
git add "pages/3_📄_要約.py"
git commit -m "feat: add summarization page"
```

---

## Task 8: 翻訳ページ

**Files:**
- Create: `pages/4_🌐_翻訳.py`

**Interfaces:**
- Consumes: `utils.gemini_client.generate_text(prompt: str) -> str`(Task 2)、`utils.prompts.build_translation_prompt(text, direction, tone) -> str`(Task 3)
- Produces: Streamlitページ。単体では他タスクから参照されない。

- [ ] **Step 1: `pages/4_🌐_翻訳.py` を実装する**

```python
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
```

- [ ] **Step 2: 起動して動作確認する**

Run: `streamlit run app.py`
Expected: サイドバーに「翻訳」ページが表示される。原文を空のまま「生成」を押すと警告が出る。原文を入力して「生成」を押すと翻訳結果が表示される。全4ページがサイドバーに揃っていることも確認する。確認後、`Ctrl+C`でサーバーを停止する。

- [ ] **Step 3: Commit**

```bash
git add "pages/4_🌐_翻訳.py"
git commit -m "feat: add translation page"
```
