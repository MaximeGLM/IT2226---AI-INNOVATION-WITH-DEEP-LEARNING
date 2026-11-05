"""Smoke test: the empty Streamlit app runs without an exception."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

MAIN_PATH = Path(__file__).resolve().parents[1] / "app" / "main.py"


def test_app_starts():
    app = AppTest.from_file(str(MAIN_PATH), default_timeout=30).run()

    assert not app.exception
    assert app.title[0].value == "DentalGuide SG"
