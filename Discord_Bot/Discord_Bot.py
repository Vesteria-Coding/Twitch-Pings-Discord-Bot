import os
import json
import requests
import time as t
from dotenv import load_dotenv

# v3
logo = r'''
  _____              _   _            _         ____    _                           ____    _                                   _     ____            _   
 |_   _| __      __ (_) | |_    ___  | |__     |  _ \  (_)  _ __     __ _   ___    |  _ \  (_)  ___    ___    ___    _ __    __| |   | __ )    ___   | |_ 
   | |   \ \ /\ / / | | | __|  / __| | '_ \    | |_) | | | | '_ \   / _` | / __|   | | | | | | / __|  / __|  / _ \  | '__|  / _` |   |  _ \   / _ \  | __|
   | |    \ V  V /  | | | |_  | (__  | | | |   |  __/  | | | | | | | (_| | \__ \   | |_| | | | \__ \ | (__  | (_) | | |    | (_| |   | |_) | | (_) | | |_ 
   |_|     \_/\_/   |_|  \__|  \___| |_| |_|   |_|     |_| |_| |_|  \__, | |___/   |____/  |_| |___/  \___|  \___/  |_|     \__,_|   |____/   \___/   \__|
                                                                    |___/                                                                                 
'''

# Setup Credentials
load_dotenv()
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
STREAMER_USERNAME = os.environ.get("STREAMER_USERNAME")
INTERVAL = 30

def get_twitch_token():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post("https://id.twitch.tv/oauth2/token", headers=headers, params=params)
    data = response.json()
    return data["access_token"]

def check_stream_status(TOKEN):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Client-Id": CLIENT_ID
    }
    response = requests.get(f"https://api.twitch.tv/helix/streams?user_login={STREAMER_USERNAME}", headers=headers)
    data = response.json()
    if data:
        if data["data"][0]["type"] == "live":
            return True
        else:
            return False

def get_steam_info(TOKEN):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Client-Id": CLIENT_ID
    }
    response = requests.get(f"https://api.twitch.tv/helix/streams?user_login={STREAMER_USERNAME}", headers=headers)
    data = response.json()
    if data:
        USERNAME = data["data"][0]["user_name"].title()
        TITLE = data["data"][0]["title"]
        return USERNAME, TITLE

def send_discord_notification():
    USERNAME, TITLE = get_steam_info(get_twitch_token())
    embed = {
        "title": f"{USERNAME} is Live!",
        "description": TITLE,
        "color": 0x9146FF
    }
    payload = {
        "content": "||@everyone||",
        "username": "Twitch Pings",
        "avatar_url": "https://github.com/Vesteria-Coding/Twitch-Pings-Discord-Bot/blob/main/Discord_Bot/Logo.png?raw=true",
        "embeds": [embed]
    }
    requests.post(WEBHOOK_URL, json=payload)

def main():
    TOKEN = get_twitch_token()
    while True:
        while not check_stream_status(TOKEN):
            print("streamer is not live")
            t.sleep(INTERVAL)
        if check_stream_status(TOKEN):
            send_discord_notification()
            while check_stream_status(TOKEN):
                print("streamer is live")
                t.sleep(INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Closing...")
        quit(0)
    except Exception as e:
        print(e)
