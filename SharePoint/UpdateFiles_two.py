import requests

tenant_id     = "xxx"
client_id     = "xxx"
client_secret = "xxx"
drive_id      = "SharePoint driveId"
file_path     = "test.zip"
target_name   = "test.zip"

# Get token
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

# Make upload session
session_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{target_name}:/createUploadSession"
r = requests.post(session_url,
    headers={"Authorization": f"Bearer {token}"}
)
upload_url = r.json()["uploadUrl"]

# fragments Upload
CHUNK = 5 * 1024 * 1024
with open(file_path, "rb") as f:
    file_size = f.seek(0,2)
    f.seek(0)
    pos = 0
    while True:
        chunk = f.read(CHUNK)
        if not chunk:
            break

        end = pos + len(chunk) - 1
        headers = {
            "Content-Length": str(len(chunk)),
            "Content-Range": f"bytes {pos}-{end}/{file_size}"
        }
        r = requests.put(upload_url, headers=headers, data=chunk)
        pos = end + 1
        print(r.status_code, r.text)
