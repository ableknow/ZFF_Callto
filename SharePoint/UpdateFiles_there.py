import os
import json
import requests

ACCESS_TOKEN = ""
USER_EMAIL = ""
LOCAL_FILE_PATH = ""
REMOTE_FOLDER = ""
CHUNK_SIZE = 50 * 1024 * 1024

# ========== Headers ==========
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}",
           "Content-Type": "application/json"}

file_name = os.path.basename(LOCAL_FILE_PATH)

folder_url = f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/drive/root/children"
folder_body = {"name": REMOTE_FOLDER, "folder": {}, "@microsoft.graph.conflictBehavior":"replace"}

r = requests.post(folder_url, headers=headers, data=json.dumps(folder_body))
if r.status_code not in (200, 201):
    print("Files Failed:", r.status_code, r.text)
else:
    print("Files OK:", REMOTE_FOLDER)

# ==========================
# UploadSession
# ==========================
upload_session_path = f"/users/{USER_EMAIL}/drive/root:/{REMOTE_FOLDER}/{file_name}:/createUploadSession"
upload_session_url = f"https://graph.microsoft.com/v1.0{upload_session_path}"
body = {"item": {"@microsoft.graph.conflictBehavior": "replace", "name": file_name}}

r = requests.post(upload_session_url, headers=headers, data=json.dumps(body))
resp_json = r.json()
if "uploadUrl" not in resp_json:
    raise ValueError(f"UploadSession Failed: {resp_json}")

upload_url = resp_json["uploadUrl"]
print("UploadSession OK")

# ==========================
# Upload
# ==========================
file_size = os.path.getsize(LOCAL_FILE_PATH)
with open(LOCAL_FILE_PATH, "rb") as f:
    start = 0
    while start < file_size:
        end = min(start + CHUNK_SIZE - 1, file_size - 1)
        f.seek(start)
        chunk = f.read(end - start + 1)

        chunk_headers = {
            "Content-Length": str(len(chunk)),
            "Content-Range": f"bytes {start}-{end}/{file_size}"
        }

        r = requests.put(upload_url, headers=chunk_headers, data=chunk)

        if r.status_code in (200, 201):
            print("OK")
            print(r.json())  # Files info look?
            break
        elif r.status_code == 202:
            next_range = r.json()["nextExpectedRanges"][0]
            start = int(next_range.split("-")[0])
            print(f"upload ok {start} / {file_size} bytes")
        else:
            raise ValueError(f"upload failed: {r.status_code}, {r.text}")
