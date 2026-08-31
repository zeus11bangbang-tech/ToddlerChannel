import json
import re
import requests

import config


SYSTEM_INSTRUCTIONS = """
You create calm educational YouTube episode plans
for toddlers ages 2 to 4.

Return ONLY valid JSON.

The JSON format must be:

{
  "title": "episode title",
  "scenes": [
    {
      "prompt": "visual action for CogVideoX",
      "narration": "simple toddler narration"
    }
  ]
}

Rules:
- 6 to 10 scenes
- one simple action per scene
- educational
- cheerful
- calm
- safe for toddlers
- use repetition
- short narration
- no violence
- no scary imagery
- no brands
- no URLs
- visual prompts must be in English
"""


def _extract_json(text: str) -> dict:

    text = text.strip()

    try:

        return json.loads(text)

    except json.JSONDecodeError:

        match = re.search(
            r"\{.*\}",
            text,
            flags=re.DOTALL
        )

        if not match:
            raise

        return json.loads(
            match.group(0)
        )


def create_episode_with_ollama(
    topic: str
) -> dict:

    prompt = (
        SYSTEM_INSTRUCTIONS
        + "\nCreate an episode about:\n"
        + topic.strip()
    )

    response = requests.post(
        config.OLLAMA_URL,
        json={
            "model":
                config.OLLAMA_MODEL,

            "prompt":
                prompt,

            "stream":
                False,
        },
        timeout=300,
    )

    response.raise_for_status()

    payload = response.json()

    return _extract_json(
        payload["response"]
    )