# tests/notifier_test.py
import pytest
from unittest.mock import MagicMock, patch
from telegram.error import TelegramError

from notifier import TelegramNotifier

class DummySettings:
    tg_bot_token = "dummy-token"
    tg_chat_id   = 12345

@patch('notifier.settings', new=DummySettings)
@patch('notifier.Bot')
def test_send_slots_success_calls_send_message(mock_bot_class):
    # Arrange
    mock_bot = MagicMock()
    mock_bot_class.return_value = mock_bot

    notifier = TelegramNotifier()
    slots = ["2025-08-10 14:00", "2025-08-11 09:00"]
    expected_text = (
        "🎯 New lesson slots available:\n"
        + "\n".join(slots)
        + "\n\nBook manually: [go to portal]"
    )

    # Act
    notifier.send_slots(slots)

    # Assert
    mock_bot.send_message.assert_called_once_with(
        chat_id=DummySettings.tg_chat_id,
        text=expected_text,
        parse_mode="Markdown"
    )
