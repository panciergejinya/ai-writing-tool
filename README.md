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

   `streamlit` コマンドが見つからない場合は `python -m streamlit run app.py` を使用してください。

## 機能一覧

- 📝 ブログ記事執筆
- ✉️ メール返信
- 📄 要約
- 🌐 翻訳(日本語⇔英語)

## テスト

```bash
pytest
```
