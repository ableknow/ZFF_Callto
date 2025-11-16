import requests

# ==========================
# Configuration
# ==========================
tenant_id     = "xxx"                # Azure AD tenant ID
client_id     = "xxx"                # Azure AD application (client) ID
client_secret = "xxx"                # Azure AD client secret
drive_id      = "yourSharePointDriveId"  # SharePoint/OneDrive drive ID
file_path     = "test.zip"           # Local file path to upload
target_name   = "test.zip"           # Target file name on SharePoint/OneDrive

# ==========================
# Get OAuth2 Access Token
# ==========================
def get_access_token():
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }
    r = requests.post(url, data=data)
    r.raise_for_status()  # Raise an error if the request failed
    return r.json()["access_token"]

token = get_access_token()

# ==========================
# Create an upload session
# ==========================
# Upload session allows uploading large files in chunks
session_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{target_name}:/createUploadSession"
r = requests.post(session_url, headers={"Authorization": f"Bearer {token}"})
r.raise_for_status()
upload_url = r.json()["uploadUrl"]  # URL for chunked upload

# ==========================
# Upload file in chunks
# ==========================
CHUNK = 5 * 1024 * 1024  # 5 MB per chunk

with open(file_path, "rb") as f:
    # Move to end of file to get total size
    f.seek(0, 2)
    file_size = f.tell()
    f.seek(0)  # Reset file pointer to beginning
    pos = 0

    while True:
        chunk = f.read(CHUNK)
        if not chunk:
            break  # End of file

        end = pos + len(chunk) - 1
        headers = {
            "Content-Length": str(len(chunk)),
            "Content-Range": f"bytes {pos}-{end}/{file_size}"  # Required by Graph API
        }

        # Upload the chunk
        r = requests.put(upload_url, headers=headers, data=chunk)

        # Check for errors
        if r.status_code not in [200, 201, 202]:
            print("Upload failed:", r.status_code, r.text)
            break

        pos = end + 1
        print(f"Uploaded {pos}/{file_size} bytes")

    # Final response after upload completes
    if r.status_code in [200, 201]:
        print("Upload complete:", r.json())
