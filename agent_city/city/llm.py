"""Tiny LLM wrapper. Uses Claude when ANTHROPIC_API_KEY is set, else returns None
so every agent can fall back to its deterministic template. The city therefore
runs end-to-end with zero setup, and gets smarter when a key is present."""
import os

MODEL = os.environ.get("CITY_MODEL", "claude-sonnet-5-5")


def available():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def ask(system, prompt, max_tokens=1200):
    if not available():
        return None
    try:
        import anthropic

        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in msg.content if b.type == "text").strip()
    except Exception as e:  # never let an API hiccup stop the city
        print(f"[llm] fallback ({e.__class__.__name__}: {e})")
        return None
