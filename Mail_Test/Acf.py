import requests
import json
import csv

# ==========================
# Config
# ==========================
tenant_id = "YOUR_TENANT_ID"
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"

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
    r.raise_for_status()
    token = r.json()["access_token"]
    return token

# ==========================
# Pull Mail
# ==========================
def fetch_all_emails(token):
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://graph.microsoft.com/v1.0/me/messages?$top=50"  # Max 50
    all_emails = []

    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        all_emails.extend(data.get("value", []))
        url = data.get("@odata.nextLink")  # Get Next Pages

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
    # type
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
# Print Text
# ==========================
def main():
    token = get_access_token()
    print("Pulling Mail...")
    emails = fetch_all_emails(token)
    print(f"Is The : {len(emails)}")
    save_as_json(emails, json_file)
    print(f"Save JSON Files: {json_file}")
    save_as_csv(emails, csv_file)
    print(f"Save CSV Files: {csv_file}")

if __name__ == "__main__":
    main()
