from dotenv import load_dotenv
import os
import base64
from requests import post
import json

load_dotenv()

# Get the CLIENT_ID and CLIENT_SECRET from the .env File
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

def get_token():
    # Combine CLIENT_ID and CLIENT_SECRET to a "Client-ID:Client-Secret"-String
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    # Spotify-API URL for the token
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,  # Korrigierter Authorization-Header
        "Content-Type": "application/x-www-form-urlencoded"  # Korrigierter Content-Type
    }

    
    data = {"grant_type": "client_credentials"}

    # Sende request
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

#Authorization header
def get_auth_header(token):
    return {"Authorization": "Bearer" + token}


token = get_token()
print("This is the access token:",token)

