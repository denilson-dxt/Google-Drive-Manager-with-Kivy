from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import threading
import time
import io
import datetime
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import os

SCOPES = ['https://www.googleapis.com/auth/drive']


class DriveManager(threading.Thread):
    def __init__(self, drive=None, file=None, files=None):
        threading.Thread.__init__(self)
        self.creds = None
        self.proccessing = False
        self.func = ""
        self.service = drive
        self.file = file
        self.files = files
        self.downloader = None
        self.status = None

    def run(self):
        if self.func == "login":
            self.login()
        elif self.func == "get_files":
            self.get_files()
        elif self.func == "download":
            self.download_file()
        elif self.func == "upload":
            self.upload_files()

    def login(self):
        self.proccessing = True
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                self.creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(self.creds, token)
        
        self.service = build("drive", "v3", credentials=self.creds)
        self.proccessing = False

    def get_files(self):
        self.proccessing = True
        results = self.service.files().list(
             fields="files(id, name, owners, createdTime, modifiedTime, iconLink, size)", pageSize=70).execute()
        self.files = results.get("files", [])

        self.proccessing = False

    def download_file(self):
        self.proccessing = True
        request = self.service.files().get_media(fileId=self.file["file_id"])
        fh = io.BytesIO()
        
        self.downloader = MediaIoBaseDownload(fh, request)
        done = False
        now = datetime.datetime.now()
        while done is False:
            self.status, done = self.downloader.next_chunk()
            with open(f"{now.year}{now.month}{now.day}{self.file['filename']}", "wb") as file:
                file.write(fh.getbuffer())
        self.proccessing = False

    def upload_files(self):
        self.proccessing = True
        for pos, file in enumerate(self.files):
            self.files[pos]["status"] = "uploading"
            file_metadata = {"name": os.path.split(file["name"])[-1]}
            media = MediaFileUpload(file["name"])
            file_upload = self.service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            self.files[pos]["status"] = "Done"
        self.proccessing = False