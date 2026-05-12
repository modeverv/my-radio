import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import context_builder

class TestContextBuilder(unittest.TestCase):

    @patch('feedparser.parse')
    def test_get_context_structure(self, mock_parse):
        # Mock RSS feed response
        mock_feed = MagicMock()
        mock_feed.entries = [
            MagicMock(title="News 1"),
            MagicMock(title="News 2"),
            MagicMock(title="News 3")
        ]
        mock_parse.return_value = mock_feed

        ctx = context_builder.get_context()
        
        self.assertIn("time", ctx)
        self.assertIn("day_of_week", ctx)
        self.assertIn("mood", ctx)
        self.assertIn("headlines", ctx)
        self.assertIsInstance(ctx["headlines"], list)
        self.assertLessEqual(len(ctx["headlines"]), 6)

    def test_mood_logic(self):
        # Test cases for mood based on hour
        test_cases = [
            (7, "morning_calm"),
            (12, "daytime_focus"),
            (19, "evening_relax"),
            (23, "late_night_chill"),
            (2, "late_night_chill")
        ]
        
        for hour, expected_mood in test_cases:
            with patch('context_builder.datetime') as mock_date:
                mock_date.now.return_value = datetime(2026, 5, 12, hour, 0)
                ctx = context_builder.get_context()
                self.assertEqual(ctx["mood"], expected_mood, f"Failed for hour {hour}")

if __name__ == '__main__':
    unittest.main()
