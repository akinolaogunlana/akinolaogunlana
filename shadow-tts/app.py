from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from preprocessing.shadow_preprocessor import PauseConfig, inject_pause_tokens
from api.piper_engine import FallbackToneEngine, PiperEngine
from audio.postprocess import postprocess_wav, wav_to_mp3

ROOT = Path(__file__).parent
MODELS = ROOT / "models"


def _engine() -> Any:
    model = MODELS / "en_US-lessac-medium.onnx"
    config = MODELS / "en_US-lessac-medium.onnx.json"
    if shutil.which("piper") and model.exists() and config.exists():
        return PiperEngine(model, config)
    return FallbackToneEngine()


def render_shadow_tts(
    text: str,
    shadow_mode: bool = True,
    pause_intensity: float = 1.0,
    pause_short: int = 700,
    pause_inversion: int = 1500,
    pause_analytical: int = 400,
) -> dict[str, str]:
    cfg = PauseConfig(
        pause_short=int(pause_short * pause_intensity),
        pause_inversion=int(pause_inversion * pause_intensity),
        pause_analytical=int(pause_analytical * pause_intensity),
    )
    if shadow_mode:
        cfg.pause_short = int(cfg.pause_short * 1.1)
        cfg.pause_inversion = int(cfg.pause_inversion * 1.15)

    prepared_text = inject_pause_tokens(text, cfg)

    tmp = Path(tempfile.mkdtemp(prefix="shadow-tts-"))
    raw_wav = tmp / "raw.wav"
    final_wav = tmp / "shadow.wav"
    final_mp3 = tmp / "shadow.mp3"

    eng = _engine()
    eng.synthesize(prepared_text, raw_wav)

    try:
        postprocess_wav(raw_wav, final_wav)
    except Exception:
        final_wav.write_bytes(raw_wav.read_bytes())

    try:
        wav_to_mp3(final_wav, final_mp3)
        mp3_path = str(final_mp3)
    except Exception:
        mp3_path = ""

    return {
        "prepared_text": prepared_text,
        "wav_path": str(final_wav),
        "mp3_path": mp3_path,
    }


def _launch_gradio() -> None:
    import gradio as gr

    with gr.Blocks(title="Shadow Psychology TTS") as demo:
        gr.Markdown("# Shadow Psychology TTS Engine")
        text = gr.Textbox(label="Script", lines=10)
        shadow = gr.Checkbox(value=True, label="Shadow Mode")
        intensity = gr.Slider(0.5, 2.0, value=1.0, step=0.1, label="Pause Intensity")
        run = gr.Button("Render")
        prepared = gr.Textbox(label="Prepared synthesis text")
        wav = gr.Audio(label="WAV Output", type="filepath")
        mp3 = gr.File(label="MP3 Output")

        def _run(t: str, s: bool, i: float):
            out = render_shadow_tts(t, s, i)
            return out["prepared_text"], out["wav_path"], out["mp3_path"] or None

        run.click(_run, [text, shadow, intensity], [prepared, wav, mp3])

    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", "7860")))


if __name__ == "__main__":
    if os.getenv("SHADOW_TTS_MODE", "gradio") == "json":
        payload = json.loads(os.getenv("SHADOW_TTS_PAYLOAD", "{}"))
        print(json.dumps(render_shadow_tts(**payload), indent=2))
    else:
        _launch_gradio()
