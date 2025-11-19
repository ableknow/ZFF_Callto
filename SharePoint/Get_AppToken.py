import requests

tenant_id = ""
client_id = ""
client_secret = ""

def get_access_token():
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }
    r = requests.post(url, data=data)
    return r.json()["access_token"]

token = get_access_token()

ACCESS_TOKEN = get_access_token()

print(ACCESS_TOKEN)
