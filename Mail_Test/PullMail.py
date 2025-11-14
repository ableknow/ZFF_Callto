import requests
import json
import csv

# ==========================
# Config
# ==========================
tenant_id = "t"
client_id = "c"
client_secret = "cs"
user_email = "user@domian"

# File name
json_file = "outlook_emails.json"
csv_file = "outlook_emails.csv"

# ==========================
# Get token 
# ==========================
def get_access_token():
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default"
    }
    r = requests.post(url, data=data)
    print("[DEBUG] Token Status:", r.status_code)
    print("[DEBUG] Token Response:", r.text)
    r.raise_for_status()
    token = r.json()["access_token"]
    return token

# ==========================
# Pull Mail
# ==========================
def fetch_all_emails(token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages?$top=50"

    print("[DEBUG] First Request URL:", url)

    all_emails = []

    while url:
        response = requests.get(url, headers=headers)
        print("[DEBUG] Status:", response.status_code)
        print("[DEBUG] Response:", response.text[:300])
        response.raise_for_status()

        data = response.json()
        all_emails.extend(data.get("value", []))
        url = data.get("@odata.nextLink")

    return all_emails

# ==========================
# Save JSON Files
# ==========================
def save_as_json(emails, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(emails, f, ensure_ascii=False, indent=2)

# ==========================
# Save CSV Files
# ==========================
def save_as_csv(emails, filename):
    if not emails:
        return
    keys = ["id", "subject", "receivedDateTime", "from", "toRecipients", "bodyPreview"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for email in emails:
            row = {
                "id": email.get("id"),
                "subject": email.get("subject"),
                "receivedDateTime": email.get("receivedDateTime"),
                "from": email.get("from", {}).get("emailAddress", {}).get("address"),
                "toRecipients": ", ".join([r.get("emailAddress", {}).get("address", "") for r in email.get("toRecipients", [])]),
                "bodyPreview": email.get("bodyPreview")
            }
            writer.writerow(row)

# ==========================
# Main
# ==========================
def main():
    token = get_access_token()
    print("Pulling Mail...")
    emails = fetch_all_emails(token)
    print(f"Total Emails: {len(emails)}")
    save_as_json(emails, json_file)
    print(f"Saved JSON: {json_file}")
    save_as_csv(emails, csv_file)
    print(f"Saved CSV: {csv_file}")

if __name__ == "__main__":
    main()
