import unittest
from pathlib import Path

from app.main import render, render_batch
from app.schemas import BatchRenderRequest, RenderRequest


class EngineTests(unittest.TestCase):
    def test_render_creates_audio_file(self) -> None:
        req = RenderRequest(text="You asked for certainty. But certainty is a defense.")
        res = render(req)
        self.assertTrue(Path(res.output_path).exists())
        self.assertGreaterEqual(len(res.segments), 2)

    def test_batch_timestamps_present(self) -> None:
        req = BatchRenderRequest(scripts=["Not comfort. Clarity."], export_timestamps=True)
        out = render_batch(req)
        self.assertTrue(out["jobs"])
        self.assertTrue(out["jobs"][0]["timestamps"])


if __name__ == "__main__":
    unittest.main()
