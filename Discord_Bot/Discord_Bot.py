import http.client
import json
import time
from urllib.parse import urlencode
from urllib.parse import urlparse

# v2.0

logo = '''
  _____              _   _            _         ____    _                           ____    _                                   _     ____            _   
 |_   _| __      __ (_) | |_    ___  | |__     |  _ \  (_)  _ __     __ _   ___    |  _ \  (_)  ___    ___    ___    _ __    __| |   | __ )    ___   | |_ 
   | |   \ \ /\ / / | | | __|  / __| | '_ \    | |_) | | | | '_ \   / _` | / __|   | | | | | | / __|  / __|  / _ \  | '__|  / _` |   |  _ \   / _ \  | __|
   | |    \ V  V /  | | | |_  | (__  | | | |   |  __/  | | | | | | | (_| | \__ \   | |_| | | | \__ \ | (__  | (_) | | |    | (_| |   | |_) | | (_) | | |_ 
   |_|     \_/\_/   |_|  \__|  \___| |_| |_|   |_|     |_| |_| |_|  \__, | |___/   |____/  |_| |___/  \___|  \___/  |_|     \__,_|   |____/   \___/   \__|
                                                                    |___/                                                                                 
'''

# Twitch API credentials
CLIENT_ID = 'Client_ID_Here'
CLIENT_SECRET = 'Client_ID_Secret_Here'

# Discord webhook URL
WEBHOOK_URL = 'Webhook_URL_Here'

# Streamer username
STREAMER_USERNAME = 'Streamer_Name_Here'

# Set & check interval
print(logo)
while True:
    print(f'How often do you want to check if {STREAMER_USERNAME} is live? (Put 0 for default):')
    timer = int(input('> '))
    if timer == 0:
        timer = 10
        break
    elif timer < 3 or timer <= 60:
        print(f'Time is set to {timer}s')
        break
    elif timer < 3:
        print('Time must be grater than 2s')
    elif timer > 60:
        print('Time must be 60s or lower')


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

# Step 3: Send notification to Discord
def send_discord_notification(stream_info):
    conn = http.client.HTTPSConnection("discord.com")

    embed = {
        "title": f"{stream_info['streamer_name']} is live!",
        "description": f"{stream_info['stream_title']}\n{stream_info['stream_url']}",
        "color": 0x9146FF  # Twitch purple
    }

    payload = json.dumps({
        "content": "@everyone",
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
        print("Notification sent successfully!")
    else:
        print(f"Failed to send notification: {response.status}, reason: {response.reason}")

# Continuous monitoring
def main():
    token = get_twitch_token()
    if token:
        print("Monitoring for live streams...")
        while True:
            stream_info = check_stream_status(token)
            if stream_info:
                send_discord_notification(stream_info)
                # Wait until the stream is offline to avoid duplicate notifications
                while check_stream_status(token):
                    time.sleep(timer)  # Check every few seconds
            else:
                print("Streamer is not live.")
            time.sleep(timer)  # Check every few seconds
    else:
        print("Failed to get Twitch token.")

if __name__ == "__main__":
    main()
