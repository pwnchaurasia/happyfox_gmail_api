import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.utils import parsedate_to_datetime
from datetime import datetime



SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GmailClient:
    def __init__(self, credentials_path=None, token_path=None):
        self.credentials_path = credentials_path or os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
        self.token_path = token_path or os.getenv('GMAIL_TOKEN_PATH', 'credentials.json')
        self.service = None
        self._authenticate()

    def _authenticate(self):
        creds = None

        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)

    def fetch_emails(self, max_results=100, query=''):
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)

            return emails
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def _get_email_details(self, message_id):
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload'].get('headers', [])
            headers_dict = {header['name']: header['value'] for header in headers}

            email_data = {
                'id': message['id'],
                'thread_id': message['threadId'],
                'from_address': headers_dict.get('From', ''),
                'to_addresses': headers_dict.get('To', ''),
                'cc_addresses': headers_dict.get('Cc', ''),
                'bcc_addresses': headers_dict.get('Bcc', ''),
                'subject': headers_dict.get('Subject', ''),
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', []),
                'is_read': 'UNREAD' not in message.get('labelIds', []),
                'is_starred': 'STARRED' in message.get('labelIds', []),
                'raw_headers': headers_dict,
                'message_body': self._get_message_body(message['payload']),
                'date_received': self._parse_date(headers_dict.get('Date', ''))
            }

            return email_data
        except HttpError as error:
            print(f'An error occurred fetching message {message_id}: {error}')
            return None

    def _get_message_body(self, payload):
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            if 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        return body

    def _parse_date(self, date_string):
        if not date_string:
            return datetime.now()

        try:
            return parsedate_to_datetime(date_string)
        except:
            return datetime.now()

    def mark_as_read(self, message_id):
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error marking message as read: {error}')
            return False

    def mark_as_unread(self, message_id):
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error marking message as unread: {error}')
            return False

    def move_to_label(self, message_id, label_name):
        try:
            labels = self.service.users().labels().list(userId='me').execute()
            label_id = None

            for label in labels.get('labels', []):
                if label['name'].lower() == label_name.lower():
                    label_id = label['id']
                    break

            if not label_id:
                return False

            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            return True
        except HttpError as error:
            print(f'Error moving message: {error}')
            return False

    def get_labels(self):
        try:
            results = self.service.users().labels().list(userId='me').execute()
            return results.get('labels', [])
        except HttpError as error:
            print(f'Error getting labels: {error}')
            return []