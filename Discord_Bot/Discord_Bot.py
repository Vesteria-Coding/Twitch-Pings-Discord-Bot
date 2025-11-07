import os
import sys
import json
import requests
import time as t
from dotenv import load_dotenv

# v3.3
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
INTERVAL = 30
CLIENT_ID = os.environ.get("CLIENT_ID")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
STREAMER_USERNAME = os.environ.get("STREAMER_USERNAME")

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
    return data.get("access_token")

def check_stream_status():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Client-Id": CLIENT_ID
    }
    response = requests.get(f"https://api.twitch.tv/helix/streams?user_login={STREAMER_USERNAME}", headers=headers)
    data = response.json()
    if data:
        if data.get("data")[0].get("type") == "live":
            return True
        else:
            return False

def get_stream_info():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Client-Id": CLIENT_ID
    }
    response = requests.get(f"https://api.twitch.tv/helix/streams?user_login={STREAMER_USERNAME}", headers=headers)
    data = response.json()
    if data:
        USERNAME = data.get("data")[0].get("user_name").title()
        TITLE = data.get("data")[0].get("title")
        URL = f'https://www.twitch.tv/{data.get("data")[0].get("user_name")}'
        GAME_ID = data.get('data')[0].get('game_id')
        response = requests.get(f"https://api.twitch.tv/helix/games?id={GAME_ID}", headers=headers)
        game_data = response.json()
        BOX_ART = game_data.get("data")[0].get('box_art_url').replace("{width}", "285").replace("{height}", "380")
        return USERNAME, TITLE, URL, BOX_ART


def send_discord_notification():
    USERNAME, TITLE, URL, BOX_ART = get_stream_info()
    embed = {
        "description": f'{TITLE}\n\n{URL}',
        "color": 0x9146FF,
        "thumbnail": {
            "url": BOX_ART
        },
        "author": {
            "name": f"{USERNAME} is Live!",
            "url": URL,
            "icon_url": f"https://avatar-resolver.vercel.app/twitch/{USERNAME}"
        }
    }
    payload = {
        "content": "||@everyone||",
        "username": "Twitch Pings",
        "avatar_url": "https://github.com/Vesteria-Coding/Twitch-Pings-Discord-Bot/blob/main/Discord_Bot/Logo.png?raw=true",
        "embeds": [embed]
    }
    requests.post(WEBHOOK_URL, json=payload)

def main():
    while True:
        while not check_stream_status():
            print("streamer is not live")
            t.sleep(INTERVAL)
        if check_stream_status():
            send_discord_notification()
            while check_stream_status():
                print("streamer is live")
                t.sleep(INTERVAL)

if __name__ == "__main__":
    TOKEN = get_twitch_token()
    try:
        main()
    except KeyboardInterrupt:
        print("Closing...")
        quit(0)
    except Exception as e:
        print(e)


