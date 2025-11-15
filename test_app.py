import pytest
from unittest.mock import patch, MagicMock
import app


def test_transcribe_audio_success():
    mock_audio_bytes = b"fake audio bytes"
    mock_transcript = "This is a transcript."

    with patch.object(
        app.client.audio.transcriptions, "create", return_value=mock_transcript
    ) as mock_create:
        result = app.transcribe_audio(mock_audio_bytes)
        assert result == mock_transcript
        mock_create.assert_called_once()
        args, kwargs = mock_create.call_args
        assert kwargs["model"] == app.STT_model


def test_transcribe_audio_failure():
    mock_audio_bytes = b"fake audio bytes"
    with patch.object(
        app.client.audio.transcriptions,
        "create",
        side_effect=Exception("API error"),
    ):
        with pytest.raises(Exception) as excinfo:
            app.transcribe_audio(mock_audio_bytes)
        assert "API error" in str(excinfo.value)
