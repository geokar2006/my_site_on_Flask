import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaInMemoryUpload
from oauth2client.service_account import ServiceAccountCredentials


def getFileByteSize(filename):
    from os import stat
    file_stats = stat(filename)
    return file_stats.st_size


def check_if_file_exist(drive_service, filename):
    file_list = drive_service.files().list(q=f"'{os.getenv('GAPI_FOLDER_ID')}' in parents", supportsAllDrives=True,
                                           includeItemsFromAllDrives=True).execute()['files']
    for i in file_list:
        if i['name'] == filename:
            return True
    return False


def upload_file(drive_service, filename, data, resumable=True, chunksize=262144):
    if check_if_file_exist(drive_service, filename):
        return
    media = MediaInMemoryUpload(data.read(), resumable=resumable, chunksize=chunksize)
    body = {"name": filename, 'kind': 'drive#fileLink', 'teamDriveId': os.getenv("DRIVE_ID"),
            'parents': [os.getenv("GAPI_FOLDER_ID")]}
    response = drive_service.files().create(supportsAllDrives=True, body=body, media_body=media).execute()


def DRIVEgetAPI(credspath):
    scope = ['https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credspath, scope)
    return build('drive', 'v3', credentials=credentials)
