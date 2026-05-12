import unittest
from unittest.mock import patch, MagicMock
import tts
import os

class TestTTS(unittest.TestCase):
    @patch('requests.post')
    @patch('tempfile.NamedTemporaryFile')
    def test_make(self, mock_tempfile, mock_post):
        # Mock VOICEVOX audio_query
        mock_query_res = MagicMock()
        mock_query_res.json.return_value = {"speedScale": 1.0}
        
        # Mock VOICEVOX synthesis
        mock_synth_res = MagicMock()
        mock_synth_res.content = b"fake wav data"
        
        mock_post.side_effect = [mock_query_res, mock_synth_res]
        
        # Mock temp file
        mock_file = MagicMock()
        mock_file.name = "/tmp/test.wav"
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        path = tts.make("Test text")
        self.assertEqual(path, "/tmp/test.wav")
        mock_file.write.assert_called_with(b"fake wav data")

    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_speak(self, mock_remove, mock_exists, mock_run):
        mock_exists.return_value = True
        
        tts.speak("/tmp/test.wav")
        
        # Check if afplay was called
        mock_run.assert_called()
        self.assertEqual(mock_run.call_args[0][0][0], "afplay")
        
        # Check if file was removed
        mock_remove.assert_called_with("/tmp/test.wav")

if __name__ == "__main__":
    unittest.main()
