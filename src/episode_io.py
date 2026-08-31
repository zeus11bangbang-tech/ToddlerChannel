from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class Scene:
    prompt: str
    narration: str


@dataclass
class Episode:
    title: str
    scenes: list[Scene]


def load_episode(path: Path) -> Episode:
    data = json.loads(path.read_text(encoding="utf-8"))

    title = str(data.get("title", "Untitled Episode")).strip()
    raw_scenes = data.get("scenes", [])

    if not raw_scenes:
        raise ValueError("Episode JSON must contain at least one scene.")

    scenes = []

    for i, item in enumerate(raw_scenes, start=1):
        prompt = str(item.get("prompt", "")).strip()
        narration = str(item.get("narration", "")).strip()

        if not prompt:
            raise ValueError(f"Scene {i} has no prompt.")

        if not narration:
            raise ValueError(f"Scene {i} has no narration.")

        scenes.append(
            Scene(
                prompt=prompt,
                narration=narration
            )
        )

    return Episode(
        title=title,
        scenes=scenes
    )