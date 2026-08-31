from pathlib import Path
import subprocess
import tempfile

import config


def _escape_ps_single_quotes(text: str) -> str:
    return text.replace("'", "''")


def synthesize_windows_sapi(text: str, output_wav: Path) -> Path:
    """
    Generates offline narration using Windows System.Speech.
    """

    output_wav.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    text = text.strip()

    if not text:
        raise ValueError("Narration text is empty.")

    safe_text = _escape_ps_single_quotes(text)

    safe_path = _escape_ps_single_quotes(
        str(output_wav.resolve())
    )

    script = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = {int(config.VOICE_RATE)}
$synth.Volume = {int(config.VOICE_VOLUME)}
$synth.SetOutputToWaveFile('{safe_path}')
$synth.Speak('{safe_text}')
$synth.Dispose()
"""

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".ps1",
        delete=False,
        encoding="utf-8"
    ) as f:

        ps1_path = Path(f.name)
        f.write(script)

    try:

        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ps1_path),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:

            raise RuntimeError(
                "Windows TTS failed.\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )

    finally:

        ps1_path.unlink(
            missing_ok=True
        )

    if not output_wav.exists():

        raise RuntimeError(
            f"TTS did not create {output_wav}"
        )

    return output_wav