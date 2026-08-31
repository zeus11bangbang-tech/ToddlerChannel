from pathlib import Path
import subprocess
import imageio_ffmpeg


def ffmpeg_path() -> str:
    return imageio_ffmpeg.get_ffmpeg_exe()


def run_ffmpeg(args):
    cmd = [
        ffmpeg_path(),
        "-y",
        *map(str, args)
    ]

    print(
        "[FFmpeg]",
        " ".join(cmd)
    )

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpeg failed.\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )


def add_narration(
    video_path: Path,
    audio_path: Path,
    output_path: Path
) -> Path:

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    run_ffmpeg([
        "-i",
        video_path,

        "-i",
        audio_path,

        "-filter_complex",
        "[0:v]tpad=stop_mode=clone:stop_duration=60[v]",

        "-map",
        "[v]",

        "-map",
        "1:a",

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "18",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-shortest",

        "-movflags",
        "+faststart",

        output_path
    ])

    return output_path


def concatenate_clips(
    clips,
    output_path: Path
) -> Path:

    if not clips:
        raise ValueError(
            "No clips were supplied."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    inputs = []

    for clip in clips:

        inputs += [
            "-i",
            str(clip)
        ]

    filter_parts = []

    for i in range(len(clips)):

        filter_parts.append(
            f"[{i}:v:0][{i}:a:0]"
        )

    concat_inputs = "".join(
        filter_parts
    )

    filter_complex = (
        f"{concat_inputs}"
        f"concat=n={len(clips)}:"
        f"v=1:a=1[v][a]"
    )

    run_ffmpeg([
        *inputs,

        "-filter_complex",
        filter_complex,

        "-map",
        "[v]",

        "-map",
        "[a]",

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "18",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-movflags",
        "+faststart",

        output_path
    ])

    return output_path