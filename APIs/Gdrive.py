import io
import os
import tempfile
import threading
import time

from flask import make_response, redirect
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaInMemoryUpload, MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials

from data import db_session
from data.items import Items
from main import app

cerd = None


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
    media = MediaInMemoryUpload(data, resumable=resumable, chunksize=chunksize)
    body = {"name": filename, 'kind': 'drive#fileLink', 'teamDriveId': os.getenv("DRIVE_ID"),
            'parents': [os.getenv("GAPI_FOLDER_ID")]}
    return drive_service.files().create(supportsAllDrives=True, body=body, media_body=media).execute()


def DRIVEgetAPI(credspath):
    global cerd
    if credspath == None:
        if cerd == None:
            return None
        return cerd
    scope = ['https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credspath, scope)
    if cerd == None:
        cerd = build('drive', 'v3', credentials=credentials)
    return build('drive', 'v3', credentials=credentials)


class Downloader(threading.Thread):
    def __init__(self, file_id, fname, type, drive, app, myid):
        super().__init__()
        self.progress = 0
        self.file_id = file_id
        self.name = fname
        self.type = type
        self.drive = drive
        self.app = app
        self.myid = myid
        self.resp = None

    def run(self):
        global responses
        request = self.drive.files().get_media(fileId=self.file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        response = False
        while not response:
            chunk = downloader.next_chunk()
            if chunk:
                status, response = chunk
                if status:
                    self.progress = int(status.progress() * 100)
        fh.seek(0)
        with self.app.app_context():
            self.resp = make_response(fh.read())
            fh.close()
            self.resp.headers.set('Content-Type', self.type)
            db_sess = db_session.create_session()
            item = db_sess.query(Items).filter(
                (Items.uploaded_file_secured_name == self.name)).first()
            self.resp.headers.set('Content-Disposition', 'attachment',
                                  filename=item.uploaded_file_name)
        self.progress = 101


class Uploader(threading.Thread):
    def __init__(self, fname, data, size, drive, app):
        super().__init__()
        self.progress = 0
        self.name = fname
        self.data = data
        self.size = size
        self.drive = drive
        self.app = app
        self.resp = None

    def run(self):
        scope = ['https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(self.app.root_path, "creds.json"), scope)
        self.drive = build('drive', 'v3', credentials=credentials)
        request = upload_file(self.drive, self.name, self.data)
        if self.size > 262144:
            try:
                response = None
                while response is None:
                    chunk = request.next_chunk()
                    if chunk:
                        status, response = chunk
                        if status:
                            self.progress = int(status.progress() * 100)
            except AttributeError:
                pass
        with self.app.app_context():
            self.resp = redirect('/')
            self.progress = 101


exporting_threads = {}
