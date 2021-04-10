import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaInMemoryUpload
from oauth2client.service_account import ServiceAccountCredentials


def getFileByteSize(filename):
    from os import stat
    file_stats = stat(filename)
    return file_stats.st_size


def upload_file(drive_service, filename, data, resumable=True, chunksize=262144):
    media = MediaInMemoryUpload(data.read(), resumable=resumable, chunksize=chunksize)
    body = {"name": filename, 'kind': 'drive#fileLink', 'teamDriveId': os.getenv("DRIVE_ID"),
            'parents': [os.getenv("UPLOADED_GAPI_ID")]}
    request = drive_service.files().create(supportsAllDrives=True, body=body, media_body=media).execute()


def DRIVEgetAPI():
    scope = ['https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    return build('drive', 'v3', credentials=credentials)
