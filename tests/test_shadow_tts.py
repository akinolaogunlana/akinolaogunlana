import importlib.util
import sys
import unittest
from pathlib import Path

SHADOW_ROOT = Path(__file__).resolve().parents[1] / "shadow-tts"
sys.path.insert(0, str(SHADOW_ROOT))

spec = importlib.util.spec_from_file_location("shadow_app", SHADOW_ROOT / "app.py")
shadow_app = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(shadow_app)

from preprocessing.shadow_preprocessor import PauseConfig, classify_line, inject_pause_tokens  # noqa: E402


class ShadowTTSTests(unittest.TestCase):
    def test_pause_injection(self):
        text = "You think you are safe. But you are avoiding evidence."
        out = inject_pause_tokens(text, PauseConfig())
        self.assertIn("<break time=\"1500ms\"/>", out)

    def test_classifier(self):
        self.assertEqual(classify_line("But you avoid facts."), "inversion")
        self.assertEqual(classify_line("Observe the structure."), "analytical")

    def test_render_outputs_wav(self):
        result = shadow_app.render_shadow_tts("Not comfort. Precision.")
        self.assertTrue(Path(result["wav_path"]).exists())


if __name__ == "__main__":
    unittest.main()
