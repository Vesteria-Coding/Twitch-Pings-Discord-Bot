from urllib.parse import urlencode
from urllib.parse import urlparse
from datetime import datetime
import http.client
import time as t
import logging
import tzlocal
import socket
import json

# v2.7

logo = r'''
  _____              _   _            _         ____    _                           ____    _                                   _     ____            _   
 |_   _| __      __ (_) | |_    ___  | |__     |  _ \  (_)  _ __     __ _   ___    |  _ \  (_)  ___    ___    ___    _ __    __| |   | __ )    ___   | |_ 
   | |   \ \ /\ / / | | | __|  / __| | '_ \    | |_) | | | | '_ \   / _` | / __|   | | | | | | / __|  / __|  / _ \  | '__|  / _` |   |  _ \   / _ \  | __|
   | |    \ V  V /  | | | |_  | (__  | | | |   |  __/  | | | | | | | (_| | \__ \   | |_| | | | \__ \ | (__  | (_) | | |    | (_| |   | |_) | | (_) | | |_ 
   |_|     \_/\_/   |_|  \__|  \___| |_| |_|   |_|     |_| |_| |_|  \__, | |___/   |____/  |_| |___/  \___|  \___/  |_|     \__,_|   |____/   \___/   \__|
                                                                    |___/                                                                                 
'''

# Twitch API credentials
CLIENT_ID = 'Twitch_Client_ID'
CLIENT_SECRET = 'Twitch_Client_ID'

# Discord webhook URL
WEBHOOK_URL = 'Twitch_Client_ID'

# Streamer username
STREAMER_USERNAME = 'Streamer_Name'

# Sidebar color
color = 0x9146FF  # Twitch purple

# Others setup
send_message = False
is_live = False

# logging setup
logging.basicConfig(
    filename="Discord_Bot.log",
    encoding="utf-8",
    filemode="a",
    format='{asctime} |:| {levelname}: {message}',
    style="{",
    datefmt="%B %d, %Y ; %I:%M %p",
    level=logging.DEBUG,
)
local_tz = tzlocal.get_localzone()

def custom_time(*args):
    return datetime.now(local_tz).timetuple()



# Set & check interval
def setup():
    print(logo)
    while True:
        print(f'How often do you want to check if {STREAMER_USERNAME} is live? (Put 0 for default):')
        try:
            timer = int(input('> '))
            if timer == 0:
                print('Using Default Timer: 30s')
                return 30
            elif 3 <= timer <= 120:
                print(f'Time Is Set To {timer}s')
                return timer
            elif timer < 3:
                print('Time Must Be 2s or More.')
            elif timer > 120:
                print('Time Must Be 120s or Lower.')
        except ValueError:
            print('Please Enter a Valid Number.')

# Step 1: Get OAuth token from Twitch
def get_twitch_token():
    conn = http.client.HTTPSConnection("id.twitch.tv")
    params = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    })
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    conn.request("POST", "/oauth2/token", params, headers)
    response = conn.getresponse()
    if response.status == 200:
        data = json.loads(response.read().decode())
        return data['access_token']
    else:
        print(f"Failed to get token: {response.status}")
        return None

# Step 2: Check if the streamer is live
def check_stream_status(token):
    global send_message
    send_message = True
    try:
        conn = http.client.HTTPSConnection("api.twitch.tv")
        headers = {
            'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {token}'
        }
        conn.request("GET", f"/helix/streams?user_login={STREAMER_USERNAME}", None, headers)
        response = conn.getresponse()
        if response.status == 200:
            data = json.loads(response.read().decode())['data']
            if data:
                # Streamer is live
                return {
                    'streamer_name': data[0]['user_name'],
                    'stream_title': data[0]['title'],
                    'stream_url': f"https://www.twitch.tv/{data[0]['user_name']}"
                }
            else:
                # Streamer is not live
                return None
        else:
            print(f"Failed to fetch stream status: {response.status}")
            return None
    except socket.gaierror:
        print('Network Error. Check Your Network Connection.')
        send_message = False
        logging.error("Network error. Check your network connection.")
    except Exception as error_message:
        print(f"An Unexpected Error Occurred With Checking Twitch's API: {error_message}.")
        send_message = False
        logging.critical(f'{error_message}.')

# Step 3: Send notification to Discord
def send_discord_notification(stream_info):
    try:
        conn = http.client.HTTPSConnection("discord.com")

        embed = {
            "title": f"{stream_info['streamer_name']} is live!",
            "description": f"{stream_info['stream_title']}\n{stream_info['stream_url']}",
            "color": color
        }

        payload = json.dumps({
            "content": "@everyone",
            "username": "Twitch Pings",
            "avatar_url": "https://github.com/Vesteria-Coding/Twitch-Pings-Discord-Bot/blob/main/Discord_Bot/Logo.png?raw=true",
            "embeds": [embed]
        })

        headers = {
            'Content-Type': 'application/json'
        }

        # Safely parse webhook path
        parsed_url = urlparse(WEBHOOK_URL)
        conn.request("POST", parsed_url.path, payload, headers)

        response = conn.getresponse()
        if response.status == 204:
            print("Notification Sent Successfully!")
            logging.debug('Notification sent successfully!')
        else:
            print(f"Failed To Send Notification: {response.status}, Reason: {response.reason}")
    except Exception as i:
        pass

# Continuous monitoring
def main():
    global is_live
    timer = setup()
    logging.info(f'Bot Start Up Monitoring {STREAMER_USERNAME}.')
    token = get_twitch_token()
    if token:
        print("Monitoring For live streams...")
        while True:
            stream_info = check_stream_status(token)
            if stream_info:
                if not is_live:
                    send_discord_notification(stream_info)
                    logging.debug('Streamer Went Live')
                    is_live = True
                # Wait until the stream is offline to avoid duplicate notifications
                while check_stream_status(token):
                    t.sleep(timer)  # Check every few seconds
            else:
                if send_message:
                    print("Streamer Is Not Live.")
                    is_live = False
            t.sleep(timer)  # Check every few seconds
    else:
        print("Failed To Get Twitch Token.")

if __name__ == "__main__":
    main()
