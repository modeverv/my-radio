import unittest
from unittest.mock import patch, MagicMock
import tts
import os

class TestTTS(unittest.TestCase):

    @patch('requests.post')
    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.remove')
    @patch('os.path.exists')
    def test_speak_success(self, mock_exists, mock_remove, mock_temp, mock_run, mock_post):
        # Mock VOICEVOX API responses
        mock_query_res = MagicMock()
        mock_query_res.json.return_value = {"dummy": "query"}
        mock_query_res.raise_for_status = MagicMock()
        
        mock_synth_res = MagicMock()
        mock_synth_res.content = b"fake_wav_data"
        mock_synth_res.raise_for_status = MagicMock()
        
        mock_post.side_effect = [mock_query_res, mock_synth_res]
        
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = "/tmp/fake.wav"
        mock_temp.return_value.__enter__.return_value = mock_file
        
        mock_exists.return_value = True

        # Call speak
        tts.speak("Hello")
        
        # Verify VOICEVOX was called
        self.assertEqual(mock_post.call_count, 2)
        # Verify afplay was called
        mock_run.assert_called_with(["afplay", "/tmp/fake.wav"], check=True)
        # Verify cleanup
        mock_remove.assert_called_with("/tmp/fake.wav")

    @patch('requests.post')
    def test_speak_failure(self, mock_post):
        # Force a connection error to VOICEVOX
        mock_post.side_effect = Exception("VOICEVOX down")
        
        # Should not raise exception
        try:
            tts.speak("Hello")
        except Exception as e:
            self.fail(f"speak() raised {type(e).__name__} unexpectedly!")

if __name__ == '__main__':
    unittest.main()
