"""第1回: LLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask --chat "LoRAとは何ですか？"

通常モードでは1回だけ質問し、
--chatを指定すると会話履歴を保ったまま続けて質問できる。
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str) -> str:
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=MODEL, contents=question)

    usage = response.usage_metadata
    prompt_tokens = usage.prompt_token_count if usage and usage.prompt_token_count is not None else "不明"
    candidates_tokens = (
        usage.candidates_token_count
        if usage and usage.candidates_token_count is not None
        else "不明"
    )
    print(f"[usage] 入力トークン数: {prompt_tokens} / 出力トークン数: {candidates_tokens}")

    return response.text

# 第1回宿題解説を参照して追加
def chat(first_question: str) -> None:
    client = genai.Client(api_key=get_api_key())
    session = client.chats.create(model=MODEL)

    question = first_question

    while question:
        response = session.send_message(question)

        usage = response.usage_metadata
        prompt_tokens = (
            usage.prompt_token_count
            if usage and usage.prompt_token_count is not None
            else "不明"
        )
        candidates_tokens = (
            usage.candidates_token_count
            if usage and usage.candidates_token_count is not None
            else "不明"
        )

        print(response.text)
        print(
            f"[usage] 入力トークン数: {prompt_tokens} "
            f"/ 出力トークン数: {candidates_tokens}"
        )

        question = input("\n[続けて質問（空行で終了）] ").strip()

def main() -> None:
    # 第1回宿題解説を参照して追加
    parser = argparse.ArgumentParser(description="LLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument(
        "--chat",
        action="store_true",
        help="会話履歴を保持して続けて質問する",
    )
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    print(f"[質問] {args.question}\n")
    try:
        if args.chat:
            chat(args.question)
        else:
            print(ask(args.question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)

if __name__ == "__main__":
    main()
