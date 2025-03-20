from dotenv import load_dotenv
import os
import base64
from requests import post
import json


# Load the environment variables from the .env file.
load_dotenv()


# Get the CLIENT_ID and CLIENT_SECRET from the .env File
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')


def get_token():
    """
    Get an access token from the API using authentications.
    
    Returns:
        str: An access token to use with the API.
    """

    # Combine CLIENT_ID and CLIENT_SECRET to a "Client-ID:Client-Secret"-String.
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    # Spotify API URL to request for a token.
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,  # Set up authentication using Base64 encoding.
        "Content-Type": "application/x-www-form-urlencoded"  # KDefine content type for the request body.
    }

    
    # Define the request body.
    data = {"grant_type": "client_credentials"}

    # Sende a POST request to get the token.
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"] # Extract the token from the response.
    return token


#Authorization header
def get_auth_header(token):
    """
    Generate an authorization header for requests using the token.
    
    Args:
        token (str): The access token.
    
    Returns:
        dict: A dictionary with the authorization header.
    """
    return {"Authorization": "Bearer" + token}


token = get_token()
print("This is the access token:",token)

