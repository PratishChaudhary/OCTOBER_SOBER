import requests


BACKBOARD_MESSAGES_URL = "https://app.backboard.io/api/threads/messages"


class BackboardError(Exception):
    pass


def generate_reply(
    user_text: str,
    api_key: str,
    assistant_id: str,
    model_name: str,
    system_prompt: str,
) -> tuple[str, list[str]]:
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "assistant_id": assistant_id,
        "content": user_text,
        "system_prompt": system_prompt,
        "llm_provider": "google",
        "model_name": model_name,
        "memory": "off",
        "stream": False,
    }

    try:
        response = requests.post(
            BACKBOARD_MESSAGES_URL,
            json=payload,
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise BackboardError("Backboard request failed") from exc

    if not isinstance(result, dict):
        raise BackboardError("Backboard returned an invalid response")

    content = result.get("content")
    if not isinstance(content, str) or not content.strip():
        raise BackboardError("Backboard returned no reply content")

    retrieved_files = result.get("retrieved_files") or []
    if not isinstance(retrieved_files, list):
        retrieved_files = []

    return content.strip(), retrieved_files