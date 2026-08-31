from pathlib import Path
import gc

import torch

from diffusers import CogVideoXPipeline
from diffusers.utils import export_to_video

import config


class CogVideoGenerator:

    def __init__(self):

        if not torch.cuda.is_available():

            raise RuntimeError(
                "CUDA was not detected."
            )

        dtype_map = {
            "bfloat16": torch.bfloat16,
            "float16": torch.float16,
            "float32": torch.float32,
        }

        dtype = dtype_map.get(
            config.DTYPE,
            torch.bfloat16
        )

        print(
            f"[CogVideoX] Loading "
            f"{config.MODEL_ID} ..."
        )

        self.pipe = (
            CogVideoXPipeline.from_pretrained(
                config.MODEL_ID,
                torch_dtype=dtype,
            )
        )

        # Important for your 12GB GPU
        if config.ENABLE_MODEL_CPU_OFFLOAD:

            self.pipe.enable_model_cpu_offload()

        else:

            self.pipe.to("cuda")

        if config.ENABLE_VAE_TILING:

            self.pipe.vae.enable_tiling()

        if (
            config.ENABLE_VAE_SLICING
            and hasattr(
                self.pipe.vae,
                "enable_slicing"
            )
        ):

            self.pipe.vae.enable_slicing()

        print("[CogVideoX] Model ready.")


    @staticmethod
    def build_prompt(
        scene_prompt: str
    ) -> str:

        return (

            f"{config.CHARACTER_BIBLE} "

            f"Scene: "
            f"{scene_prompt.strip()} "

            f"Visual style: "
            f"{config.STYLE_BIBLE}."
        )


    def generate(
        self,
        scene_prompt: str,
        output_path: Path,
        seed: int
    ):

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        full_prompt = (
            self.build_prompt(
                scene_prompt
            )
        )

        print(
            f"[CogVideoX] Generating: "
            f"{output_path.name}"
        )

        print(
            f"[Prompt] {full_prompt}"
        )

        kwargs = {

            "prompt":
                full_prompt,

            "num_videos_per_prompt":
                1,

            "num_inference_steps":
                config.NUM_INFERENCE_STEPS,

            "num_frames":
                config.NUM_FRAMES,

            "guidance_scale":
                config.GUIDANCE_SCALE,

            "generator":
                torch.Generator(
                    device="cuda"
                ).manual_seed(seed)
        }

        video = self.pipe(
            **kwargs
        ).frames[0]

        export_to_video(
            video,
            str(output_path),
            fps=config.FPS
        )

        del video

        gc.collect()

        torch.cuda.empty_cache()

        return output_path