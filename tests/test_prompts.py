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
