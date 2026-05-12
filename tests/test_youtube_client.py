import unittest
from unittest.mock import patch, MagicMock
import youtube_client

class TestYouTubeClient(unittest.TestCase):

    @patch('feedparser.parse')
    def test_get_candidate_tracks_success(self, mock_parse):
        # Mock RSS feed response
        mock_feed = MagicMock()
        mock_entry = MagicMock()
        mock_entry.title = "Official髭男dism - Same Blue"
        mock_feed.entries = [mock_entry] * 20
        mock_parse.return_value = mock_feed

        tracks = youtube_client.get_candidate_tracks("morning_calm")
        
        self.assertEqual(len(tracks), 15)  # Should return random sample of 15
        self.assertEqual(tracks[0]["artist"], "Official髭男dism")
        self.assertEqual(tracks[0]["title"], "Same Blue")

    @patch('feedparser.parse')
    def test_get_candidate_tracks_fallback(self, mock_parse):
        # Force an exception
        mock_parse.side_effect = Exception("RSS error")
        
        tracks = youtube_client.get_candidate_tracks("morning_calm")
        
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]["title"], "Jazz")

if __name__ == '__main__':
    unittest.main()
