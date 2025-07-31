# Driving Lesson Slot Watcher

Automated watcher that refreshes a driving lesson booking portal, detects newly opened slots, and notifies you via Telegram. Built with stealthy browser automation, diffing, scheduling, and observability.

## Prerequisites

- Conda (Miniconda or Anaconda)
- Telegram bot token and target chat ID (send `/start` to your bot and note the chat ID)
- Valid portal credentials
- Optional: TOTP secret if the portal uses MFA

## Setup with Conda

1. **Create and activate the environment**

```bash
conda env create -f environment.yml
conda activate CDCbooker
```
