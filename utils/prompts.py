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
