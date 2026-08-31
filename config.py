from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent

EPISODES_DIR = ROOT / "episodes"

OUTPUT_DIR = ROOT / "output"


# ============================================================
# COGVIDEOX MODEL SETTINGS
# ============================================================

MODEL_ID = "THUDM/CogVideoX-5b"

# CogVideoX-5B was trained in bfloat16
DTYPE = "bfloat16"


# ============================================================
# VIDEO GENERATION SETTINGS
# ============================================================

# Standard CogVideoX-5B frame count
NUM_FRAMES = 49

# Standard playback rate
FPS = 8

# Higher = slower but usually better quality
NUM_INFERENCE_STEPS = 50

# How strongly the model follows the prompt
GUIDANCE_SCALE = 6.0

# Leave these as None to use the model defaults
WIDTH = None
HEIGHT = None


# ============================================================
# RANDOM SEED
# ============================================================

# Keeping a fixed seed helps make results more repeatable
BASE_SEED = 42


# ============================================================
# GPU / MEMORY SETTINGS
# ============================================================

# Important for a 12 GB GPU
ENABLE_MODEL_CPU_OFFLOAD = True

# Reduces VAE memory usage
ENABLE_VAE_TILING = True

# Additional VAE memory optimization
ENABLE_VAE_SLICING = True

# Leave False unless you run out of VRAM during VAE decoding
# Setting this True will make generation slower
FORCE_VAE_CPU = False


# ============================================================
# CHARACTER DESCRIPTION
# ============================================================

CHARACTER_BIBLE = (
    "Milo is a small friendly blue teddy bear with rounded ears, "
    "large gentle brown eyes, soft plush fur, and a tiny yellow backpack. "
    "Milo always has the same face, same blue fur, same yellow backpack, "
    "same proportions, and the same preschool cartoon appearance."
)


# ============================================================
# VISUAL STYLE
# ============================================================

STYLE_BIBLE = (
    "high-quality toddler-friendly 3D preschool cartoon, "
    "soft rounded shapes, "
    "bright cheerful colors, "
    "simple uncluttered backgrounds, "
    "soft lighting, "
    "slow gentle movement, "
    "friendly expressions, "
    "child-safe visual design, "
    "no scary imagery, "
    "no violence, "
    "no text, "
    "no logos, "
    "no watermark"
)


# ============================================================
# WINDOWS TEXT TO SPEECH
# ============================================================

# Windows SpeechSynthesizer rate
# Usually ranges from -10 to 10
VOICE_RATE = -1

# Volume ranges from 0 to 100
VOICE_VOLUME = 100


# ============================================================
# OPTIONAL OLLAMA EPISODE WRITER
# ============================================================

# Keep False for now.
# Later we can turn this on so a local AI automatically
# writes episode scripts from a simple topic.
USE_OLLAMA = False

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

OLLAMA_MODEL = "llama3.2:3b"