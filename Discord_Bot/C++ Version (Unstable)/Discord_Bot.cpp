#include "INIReader.h"
#include <iostream>
#include <string>
#include <cpr/cpr.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

std::string get_twitch_token(std::string CLIENT_ID, std::string ClIENT_ID_SECRET) {
    cpr::Response r = cpr::Post(
        cpr::Url{"https://id.twitch.tv/oauth2/token"},
        cpr::Header{{"Content-Type", "application/x-www-form-urlencoded"}},
        cpr::Payload{
            {"client_id", CLIENT_ID},
            {"client_secret", ClIENT_ID_SECRET},
            {"grant_type", "client_credentials"}
        }
    );
    json data = json::parse(r.text);
    std::string token = data["access_token"].get<std::string>();
    return token;
}

bool check_stream_status(std::string TOKEN, std::string STREAMER_USERNAME) {
    cpr::Response r = cpr::Post(
        cpr::Url{"https://api.twitch.tv/helix/streams?user_login=" + STREAMER_USERNAME}
    );
    return true;
}

int main() {
    INIReader reader("config.ini");
    const std::string CLIENT_ID = reader.Get("settings", "CLIENT_ID", "Error");
    const std::string CLIENT_ID_SECRET = reader.Get("settings", "CLIENT_ID_SECRET", "Error");
    const std::string TOKEN = get_twitch_token(CLIENT_ID, CLIENT_ID_SECRET);
    return 0;
}
