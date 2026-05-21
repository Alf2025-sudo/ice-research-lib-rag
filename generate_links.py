import os
import csv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
# Replace with your actual Google Drive Folder ID (found in the folder's URL)
FOLDER_ID = '1a6F-TSSB_sA-1No6H90mPCfbxbT0pvpE' 

def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API to list files in the specific folder
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed = false",
        fields="nextPageToken, files(id, name)",
        pageSize=1000
    ).execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
        return

    with open('file_mapping.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['filename', 'drive_id'])
        for item in items:
            writer.writerow([item['name'], item['id']])
            
    print("✅ file_mapping.csv successfully generated!")

if __name__ == '__main__':
    main()