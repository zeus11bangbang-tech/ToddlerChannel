from pathlib import Path
import argparse
import json
import re

import config
from src.episode_io import load_episode
from src.video_generator import CogVideoGenerator
from src.tts import synthesize_windows_sapi
from src.media import add_narration, concatenate_clips
from src.ollama_writer import create_episode_with_ollama


def safe_name(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_-]+", "_", text.strip())
    return text.strip("_") or "episode"


def create_episode_json_from_topic(topic: str, output_json: Path):
    if not config.USE_OLLAMA:
        raise RuntimeError(
            "USE_OLLAMA is False in config.py. "
            "Either set it True after installing Ollama, or provide --episode."
        )

    data = create_episode_with_ollama(topic)

    output_json.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"[Writer] Created {output_json}")
    return output_json


def build_episode(episode_json: Path):
    episode = load_episode(episode_json)

    episode_dir = config.OUTPUT_DIR / safe_name(episode.title)
    raw_dir = episode_dir / "raw_video"
    audio_dir = episode_dir / "audio"
    voiced_dir = episode_dir / "voiced_scenes"

    for folder in [raw_dir, audio_dir, voiced_dir]:
        folder.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Building: {episode.title} ===")
    print(f"Scenes: {len(episode.scenes)}")
    print(f"Output folder: {episode_dir}\n")

    # IMPORTANT:
    # Load CogVideoX once instead of reloading it for every scene.
    generator = CogVideoGenerator()

    voiced_clips = []

    for index, scene in enumerate(episode.scenes, start=1):

        stem = f"scene_{index:02d}"

        raw_video = raw_dir / f"{stem}.mp4"
        narration_wav = audio_dir / f"{stem}.wav"
        voiced_video = voiced_dir / f"{stem}.mp4"

        # VIDEO
        if not raw_video.exists():

            generator.generate(
                scene_prompt=scene.prompt,
                output_path=raw_video,
                seed=config.BASE_SEED + index - 1,
            )

        else:
            print(f"[Skip] Existing video: {raw_video.name}")

        # VOICE
        if not narration_wav.exists():

            print(f"[TTS] {scene.narration}")

            synthesize_windows_sapi(
                scene.narration,
                narration_wav
            )

        else:
            print(
                f"[Skip] Existing narration: "
                f"{narration_wav.name}"
            )

        # COMBINE VIDEO + VOICE
        if not voiced_video.exists():

            add_narration(
                raw_video,
                narration_wav,
                voiced_video
            )

        else:
            print(
                f"[Skip] Existing voiced scene: "
                f"{voiced_video.name}"
            )

        voiced_clips.append(voiced_video)

    # FINAL EPISODE
    final_path = (
        episode_dir
        / f"{safe_name(episode.title)}_FINAL.mp4"
    )

    concatenate_clips(
        voiced_clips,
        final_path
    )

    print("\n========================================")
    print("DONE")
    print(f"Final video: {final_path}")
    print("========================================\n")

    return final_path


def main():

    parser = argparse.ArgumentParser(
        description="Local AI toddler-video production pipeline."
    )

    group = parser.add_mutually_exclusive_group(
        required=True
    )

    group.add_argument(
        "--episode",
        type=Path,
        help="Path to an episode JSON file.",
    )

    group.add_argument(
        "--topic",
        type=str,
        help=(
            "Create an episode JSON using local Ollama, "
            "then render it."
        ),
    )

    args = parser.parse_args()

    if args.topic:

        filename = (
            safe_name(args.topic[:60])
            + ".json"
        )

        episode_json = (
            config.EPISODES_DIR
            / filename
        )

        if not episode_json.exists():

            create_episode_json_from_topic(
                args.topic,
                episode_json
            )

    else:

        episode_json = args.episode

    build_episode(episode_json)


if __name__ == "__main__":
    main()