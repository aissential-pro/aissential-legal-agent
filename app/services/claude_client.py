import time
from anthropic import Anthropic, APIError
from app.config.settings import settings


client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def ask_claude(system_prompt: str, user_prompt: str, retries: int = 3) -> str:
    """
    Send a prompt to Claude and return the response.

    Implements exponential backoff retry on APIError.

    Args:
        system_prompt: The system prompt to set Claude's behavior
        user_prompt: The user's message/query
        retries: Number of retry attempts on failure (default: 3)

    Returns:
        The text response from Claude

    Raises:
        APIError: If all retry attempts fail
    """
    last_error = None

    for attempt in range(retries):
        try:
            message = client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return message.content[0].text
        except APIError as e:
            last_error = e
            if attempt < retries - 1:
                # Exponential backoff: 1s, 2s, 4s, etc.
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            continue

    raise last_error
