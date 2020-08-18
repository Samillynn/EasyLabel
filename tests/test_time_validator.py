import sys
from pathlib import Path
from unittest import TestCase


here = Path(__file__).parent.resolve().parent

sys.path.insert(0, str(here))

from label_file_parser import valid_time_format


class test_time(TestCase):
    def test_valid_time_1(self):
        self.assertTrue(valid_time_format("1"))
        self.assertTrue(valid_time_format("1.2"))
        self.assertTrue(valid_time_format("1.5"))
        self.assertTrue(valid_time_format("1.05"))
        self.assertTrue(valid_time_format("1.50"))
        self.assertTrue(valid_time_format("1.500"))
        self.assertTrue(valid_time_format("1.125"))
        self.assertTrue(valid_time_format("12.1"))
        self.assertTrue(valid_time_format("13.10"))
        self.assertTrue(valid_time_format("19.99"))
        self.assertTrue(valid_time_format("99.00"))

    def test_valid_time_2(self):
        self.assertTrue(valid_time_format("00:01"))
        self.assertTrue(valid_time_format("0:1"))
        self.assertTrue(valid_time_format("0:10"))
        self.assertTrue(valid_time_format("00:01"))
        self.assertTrue(valid_time_format("01:00"))
        self.assertTrue(valid_time_format("10:00"))
        self.assertTrue(valid_time_format("59:59"))
        self.assertTrue(valid_time_format("12:3.3"))
        self.assertTrue(valid_time_format("12:34.56"))
        self.assertTrue(valid_time_format("7:08.910"))
        self.assertTrue(valid_time_format("7:8.9"))
        self.assertTrue(valid_time_format("02:08.00"))
        self.assertTrue(valid_time_format("02:08.001"))
        self.assertTrue(valid_time_format("02:08.125"))
        self.assertTrue(valid_time_format("02:08.50"))

    def test_invalid_time(self):
        self.assertFalse(valid_time_format("02;02"))
        self.assertFalse(valid_time_format("12:12:12"))
        self.assertFalse(valid_time_format("12.9999"))
        self.assertFalse(valid_time_format("1:65"))
        self.assertFalse(valid_time_format("999:1"))
        self.assertFalse(valid_time_format("60:60"))
        self.assertFalse(valid_time_format("12.12.30"))
        self.assertFalse(valid_time_format("0..9"))
        self.assertFalse(valid_time_format("9.0.0"))
        self.assertFalse(valid_time_format("123:2"))
        self.assertFalse(valid_time_format("1990"))
        self.assertFalse(valid_time_format("34 03"))
        self.assertFalse(valid_time_format("00~19"))
        self.assertFalse(valid_time_format("00:00:00:00"))
        self.assertFalse(valid_time_format("6[07"))
        self.assertFalse(valid_time_format("02\03"))
        self.assertFalse(valid_time_format("02/03"))
        self.assertFalse(valid_time_format("02：03"))
        self.assertFalse(valid_time_format("02。03"))
        self.assertFalse(valid_time_format("02；03"))
        self.assertFalse(valid_time_format("02·03"))
