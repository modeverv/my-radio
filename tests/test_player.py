import unittest
from unittest.mock import patch, MagicMock
import player

class TestPlayer(unittest.TestCase):

    @patch('subprocess.run')
    def test_search_and_play_success(self, mock_run):
        # Mock osascript returning "true"
        mock_run.return_value.stdout = "true"
        mock_run.return_value.returncode = 0
        
        result = player.search_and_play("Test Query")
        self.assertTrue(result)
        # Check if osascript was called
        self.assertEqual(mock_run.call_args[0][0][0], "osascript")

    @patch('subprocess.run')
    def test_search_and_play_failure(self, mock_run):
        # Mock osascript returning "false"
        mock_run.return_value.stdout = "false"
        
        result = player.search_and_play("Missing Song")
        self.assertFalse(result)

    @patch('subprocess.run')
    def test_get_now_playing_active(self, mock_run):
        # Mock osascript returning track info
        mock_run.return_value.stdout = "Song Title||Artist Name||180.5"
        
        info = player.get_now_playing()
        self.assertEqual(info["title"], "Song Title")
        self.assertEqual(info["artist"], "Artist Name")
        self.assertEqual(info["duration"], 180.5)

    @patch('subprocess.run')
    def test_get_now_playing_inactive(self, mock_run):
        # Mock osascript returning "not_playing"
        mock_run.return_value.stdout = "not_playing"
        
        info = player.get_now_playing()
        self.assertEqual(info["title"], "Unknown")

if __name__ == '__main__':
    unittest.main()
