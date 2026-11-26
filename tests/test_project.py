import os
import runpy
import unittest
from pathlib import Path
os.environ["QT_QPA_PLATFORM"] = "offscreen"
ns = runpy.run_path(str(Path(__file__).resolve().parents[1] / "Lazy_Clock-New.py"))
bounded = ns["bounded"]
as_bool = ns["as_bool"]

class SettingsTests(unittest.TestCase):
    def test_bounds(self):
        self.assertEqual(bounded(1000, 500, 180, 700), 700)
        self.assertEqual(bounded(0, 500, 180, 700), 180)
        self.assertEqual(bounded("350", 500, 180, 700), 350)

    def test_invalid_values(self):
        for value in (None, "invalid", float("inf")):
            self.assertEqual(bounded(value, 500, 180, 700), 500)

    def test_boolean_settings(self):
        for value in (True, "TRUE", "1", "yes"):
            self.assertTrue(as_bool(value))
        for value in (False, "0", "no", None):
            self.assertFalse(as_bool(value))

    def test_default_colors(self):
        from PySide6.QtGui import QColor
        for key in ("hour_color", "minute_color", "second_color"):
            self.assertTrue(QColor(ns["DEFAULTS"][key]).isValid())
