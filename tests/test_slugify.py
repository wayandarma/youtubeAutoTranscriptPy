#!/usr/bin/env python3
"""
Unit tests for the slugify function in transcript_extractor.py
"""

import unittest
from transcript_extractor import slugify

class TestSlugify(unittest.TestCase):
    def test_basic_slugification(self):
        """Test basic slugification of simple strings"""
        self.assertEqual(slugify("Hello World"), "hello_world")
        self.assertEqual(slugify("Test Case"), "test_case")
        self.assertEqual(slugify("simple"), "simple")

    def test_special_characters(self):
        """Test handling of special characters"""
        self.assertEqual(slugify("Special & Characters @#$%"), "special_characters")
        self.assertEqual(slugify("Hello-World!"), "hello_world")
        self.assertEqual(slugify("Test.Case"), "test_case")

    def test_spaces_and_underscores(self):
        """Test handling of spaces and underscores"""
        self.assertEqual(slugify("  Multiple   Spaces  "), "multiple_spaces")
        self.assertEqual(slugify("___underscores___"), "underscores")
        self.assertEqual(slugify("mixed   spaces_and___underscores"), "mixed_spaces_and_underscores")

    def test_unicode_characters(self):
        """Test handling of Unicode characters"""
        self.assertEqual(slugify("Café au Lait"), "cafe_au_lait")
        self.assertEqual(slugify("你好世界"), "你好世界")
        self.assertEqual(slugify("Café & 你好"), "cafe_你好")

    def test_long_titles(self):
        """Test handling of long titles"""
        long_title = "a" * 200
        self.assertEqual(len(slugify(long_title)), 100)
        self.assertEqual(slugify(long_title), "a" * 100)

    def test_edge_cases(self):
        """Test edge cases"""
        self.assertEqual(slugify(""), "")
        self.assertEqual(slugify("   "), "")
        self.assertEqual(slugify("!@#$%"), "")
        self.assertEqual(slugify("123"), "123")
        self.assertEqual(slugify("---"), "")

    def test_mixed_case(self):
        """Test handling of mixed case"""
        self.assertEqual(slugify("MiXeD CaSe"), "mixed_case")
        self.assertEqual(slugify("UPPERCASE"), "uppercase")
        self.assertEqual(slugify("lowercase"), "lowercase")

if __name__ == '__main__':
    unittest.main() 