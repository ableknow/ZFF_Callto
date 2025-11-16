import requests
from urllib.parse import urlparse

# =========================
# Config
# =========================
tenant_id     = "t"
client_id     = "c"
client_secret = "cs"
sharepoint_url = "https://name.sharepoint.com/sites"

# =========================
# Get Access Token
# =========================
def get_token():
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default"
    }
    r = requests.post(url, data=data)
    if r.status_code != 200:
        raise Exception(f"Pull Access Token failed: {r.status_code}, {r.text}\n"
                        f"Pls Check client_id, client_secret is true.")
    return r.json()["access_token"]

# =========================
# Get siteId
# =========================
def get_site_id(sp_url, token):
    headers = {"Authorization": f"Bearer {token}"}
    parsed = urlparse(sp_url)
    host = parsed.netloc
    path = parsed.path.rstrip("/")  # Del end /
    api_url = f"https://graph.microsoft.com/v1.0/sites/{host}:{path}?$select=id"
    
    r = requests.get(api_url, headers=headers)
    if r.status_code == 401:
        raise Exception("401 Unauthorized: Access Token failed SharePoint，"
                        "Have? App/Api Graph Api Sites.Read.All & Sites.ReadWrite.All SharePoint Api Sites.Read.All & Sites.ReadWrite.All")
    elif r.status_code != 200:
        raise Exception(f"Pull siteId failed: {r.status_code}, {r.text}")
    
    return r.json()["id"]

# =========================
# Main
# =========================
def main():
    token = get_token()
    print("✅ Access Token OK!")
    
    site_id = get_site_id(sharepoint_url, token)
    print("✅ siteId:", site_id)

if __name__ == "__main__":
    main()
