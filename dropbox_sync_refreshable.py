import os
import json
import time
import requests
import dropbox

# Load credentials from local file
with open("dropbox_credentials_refresh.txt") as f:
    creds = dict(line.strip().split("=", 1) for line in f if "=" in line)

APP_KEY = creds["APP_KEY"]
APP_SECRET = creds["APP_SECRET"]
REFRESH_TOKEN = creds["REFRESH_TOKEN"]
DEST_FOLDER = "vault/memory/"
SOURCE_FOLDER = "/Full Court Docket Files"

def refresh_access_token():
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    auth = (APP_KEY, APP_SECRET)
    response = requests.post(url, data=data, auth=auth)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Token refresh failed: {response.text}")

def sync_files():
    access_token = refresh_access_token()
    dbx = dropbox.Dropbox(access_token)
    os.makedirs(DEST_FOLDER, exist_ok=True)

    try:
        entries = dbx.files_list_folder(SOURCE_FOLDER).entries
    except Exception as e:
        print(f"Failed to list folder: {e}")
        return

    for entry in entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            filename = entry.name
            dest_path = os.path.join(DEST_FOLDER, filename)

            try:
                metadata, res = dbx.files_download(entry.path_display)
                with open(dest_path, "wb") as f:
                    f.write(res.content)
                print(f"Downloaded: {filename}")
            except Exception as e:
                print(f"Failed to download {filename}: {e}")

if __name__ == "__main__":
    sync_files()
