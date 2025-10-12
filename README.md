# 🎮 Twitch to Discord Bot

This bot monitors a Twitch streamer and sends live notifications to a Discord channel, including stream info and game box art.

---

## Getting Started

### 1. Install Dependencies
Run the provided `Install.bat` to install all required Python packages.

---

### 2. Set Up the Bot Script
- Copy `Discord_Bot.py` into your preferred Python editor (e.g., PyCharm).
- Ensure your `.env` file or in-script variables contain the correct credentials.

---

### 3. Create a Discord Webhook
1. Go to [Discord Webhooks](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).
2. Copy the webhook URL.
3. Replace `WEBHOOK_URL_HERE` in the code or `.env` file with your webhook URL.

---

### 4. Create a Twitch App (Bot)
1. Go to [Twitch Developer Portal](https://dev.twitch.tv/authentication/register-app/).
2. Register a new application.
3. Copy the **Client ID** and **Client Secret**.
4. Replace `CLIENT_ID` and `CLIENT_SECRET` in the code or `.env` file.

---

### 5. Set the Streamer to Monitor
- Replace `STREAMER_USERNAME` with the Twitch username you want to track.

---

### 6. Run the Bot
- Run the Python script in your editor of choice.
- The bot will send Discord notifications whenever the streamer goes live.

---

## ✅ Enjoy!
Your Discord will now receive live notifications with stream information and game box art automatically.
