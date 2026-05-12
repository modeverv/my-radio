import unittest
from unittest.mock import patch, MagicMock
import json
from llm_director import get_direction

class TestLLMDirector(unittest.TestCase):
    @patch('llm_director.client.chat.completions.create')
    def test_get_direction_success(self, mock_create):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "mc_script": "Hello listeners!",
                "show_title": "Morning Show"
            })))
        ]
        mock_create.return_value = mock_response
        
        context = {
            "time": "08:00",
            "day_of_week": "Monday",
            "mood": "morning_calm",
            "headlines": ["News A", "News B"]
        }
        previous_track = {"title": "Song 1", "artist": "Artist 1"}
        
        result = get_direction(context, previous_track)
        
        self.assertEqual(result["mc_script"], "Hello listeners!")
        self.assertEqual(result["show_title"], "Morning Show")

    @patch('llm_director.client.chat.completions.create')
    def test_get_direction_fallback(self, mock_create):
        # Mock error to trigger fallback
        mock_create.side_effect = Exception("API Error")
        
        context = {"headlines": []}
        result = get_direction(context)
        
        self.assertEqual(result["show_title"], "デフォルト放送")
        self.assertIn("mc_script", result)

if __name__ == "__main__":
    unittest.main()
