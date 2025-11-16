import requests
from urllib.parse import urlparse

# =========================
# Configuration
# =========================
tenant_id = "YOUR_TENANT_ID"
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
sharepoint_url = "https://yourdomain.sharepoint.com/sites/yoursite"
doc_library = "Documents"  # Name of the document library

# =========================
# Get Access Token
# =========================
def get_token():
    """
    Get an Access Token from Azure AD using Client Credentials flow
    """
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default"
    }
    r = requests.post(url, data=data)
    if r.status_code != 200:
        raise Exception(f"Failed to get Access Token: {r.status_code}, {r.text}")
    return r.json()["access_token"]

# =========================
# Get siteId
# =========================
def get_site_id(sp_url, token):
    """
    Get the SharePoint siteId using the site URL
    :param sp_url: Full SharePoint site URL
    :param token: Access Token
    :return: siteId as string
    """
    headers = {"Authorization": f"Bearer {token}"}
    parsed = urlparse(sp_url)
    host = parsed.netloc
    path = parsed.path.rstrip("/")  # Remove trailing slash
    api_url = f"https://graph.microsoft.com/v1.0/sites/{host}:{path}?$select=id"
    
    r = requests.get(api_url, headers=headers)
    if r.status_code != 200:
        raise Exception(f"Failed to get siteId: {r.status_code}, {r.text}")
    return r.json()["id"]

# =========================
# Get driveId (Document Library)
# =========================
def get_drive_id(site_id, token, library_name="Documents"):
    """
    Get the driveId (document library ID) for a SharePoint site
    :param site_id: siteId from SharePoint
    :param token: Access Token
    :param library_name: Name of the document library
    :return: driveId as string
    """
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    r = requests.get(api_url, headers=headers)
    
    if r.status_code != 200:
        raise Exception(f"Failed to get driveId: {r.status_code}, {r.text}")
    
    drives = r.json().get("value", [])
    for d in drives:
        if d["name"].lower() == library_name.lower():
            return d["id"]
    
    # If the specified library is not found, list available libraries
    available = [d["name"] for d in drives]
    raise Exception(f"Document library '{library_name}' not found. Available libraries: {available}")

# =========================
# Main flow
# =========================
def main():
    token = get_token()
    print("✅ Access Token retrieved successfully")
    
    site_id = get_site_id(sharepoint_url, token)
    print("✅ siteId:", site_id)
    
    drive_id = get_drive_id(site_id, token, doc_library)
    print("✅ driveId:", drive_id)

if __name__ == "__main__":
    main()
