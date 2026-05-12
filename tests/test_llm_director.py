import unittest
from unittest.mock import patch, MagicMock
import llm_director
import json

class TestLLMDirector(unittest.TestCase):

    @patch('llm_director.client.chat.completions.create')
    def test_get_direction_success(self, mock_create):
        # Mock successful LLM response with JSON in markdown block
        mock_response = MagicMock()
        expected_json = {
            "playlist": [{"title": "Test Song", "artist": "Test Artist"}],
            "mc_script": "Test script",
            "show_title": "Test Show"
        }
        mock_response.choices[0].message.content = "```json\n" + json.dumps(expected_json) + "\n```"
        mock_create.return_value = mock_response

        ctx = {"time": "12:00", "mood": "daytime_focus"}
        candidates = [{"title": "C1", "artist": "A1"}]
        
        result = llm_director.get_direction(ctx, candidates)
        
        self.assertEqual(result["show_title"], "Test Show")
        self.assertEqual(len(result["playlist"]), 1)

    @patch('llm_director.client.chat.completions.create')
    def test_get_direction_fallback(self, mock_create):
        # Mock LLM returning invalid JSON
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Not a JSON"
        mock_create.return_value = mock_response

        ctx = {"time": "12:00", "mood": "daytime_focus"}
        candidates = []
        
        result = llm_director.get_direction(ctx, candidates)
        
        # Should return fallback
        self.assertEqual(result["show_title"], "デフォルト放送")

if __name__ == '__main__':
    unittest.main()
