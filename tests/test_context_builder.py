import unittest
from unittest.mock import patch, MagicMock
from context_builder import NewsManager, get_context

class TestContextBuilder(unittest.TestCase):
    @patch('random.shuffle')
    def test_news_manager_get_next_headlines(self, mock_shuffle):
        nm = NewsManager()
        nm.headlines = ["News 1", "News 2", "News 3", "News 4"]
        nm.current_index = 0
        
        # Test getting 3 headlines
        h1 = nm.get_next_headlines(3)
        self.assertEqual(len(h1), 3)
        self.assertEqual(h1, ["News 1", "News 2", "News 3"])
        self.assertEqual(nm.current_index, 3)
        
        # Test wrapping around (ring queue)
        h2 = nm.get_next_headlines(2)
        self.assertEqual(len(h2), 2)
        self.assertEqual(h2, ["News 4", "News 1"])
        self.assertEqual(nm.current_index, 1)
        # Should be called once when index reset to 0
        mock_shuffle.assert_called_once()

    def test_get_context(self):
        with patch('context_builder.news_manager.get_next_headlines') as mock_get:
            mock_get.return_value = ["Mock News 1", "Mock News 2", "Mock News 3"]
            ctx = get_context()
            
            self.assertIn("time", ctx)
            self.assertIn("day_of_week", ctx)
            self.assertIn("mood", ctx)
            self.assertEqual(ctx["headlines"], ["Mock News 1", "Mock News 2", "Mock News 3"])

if __name__ == "__main__":
    unittest.main()
