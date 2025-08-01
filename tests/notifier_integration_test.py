# tests/test_notifier_integration.py
import time
import asyncio
import pytest
from notifier import TelegramNotifier

@pytest.mark.integration
def test_send_slots_via_telegram_and_leave_message():
    notifier = TelegramNotifier()
    
    # craft a unique payload so you can spot it
    ts = int(time.time())
    test_slot = f"🎯 Integration-test slot at {ts}"
    
    # send the message and await the coroutine
    msg = asyncio.run(
        notifier.bot.send_message(
            chat_id=notifier.chat_id,
            text=test_slot
        )
    )
    
    # basic sanity checks
    assert str(msg.chat.id) == str(notifier.chat_id)
    assert test_slot in msg.text
    
    # print the message_id so you can find it in Telegram
    print(f"🔔 Integration test message sent! message_id={msg.message_id}")
