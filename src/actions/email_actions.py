from actions.base import Action
from typing import Any, Dict


class MarkAsReadAction(Action):
    def execute(self, email_id: str, gmail_client: Any, **kwargs) -> Dict:
        success = gmail_client.mark_as_read(email_id)
        return {
            'action': 'mark_as_read',
            'success': success,
            'email_id': email_id
        }

    def get_name(self) -> str:
        return "mark_as_read"


class MarkAsUnreadAction(Action):
    def execute(self, email_id: str, gmail_client: Any, **kwargs) -> Dict:
        success = gmail_client.mark_as_unread(email_id)
        return {
            'action': 'mark_as_unread',
            'success': success,
            'email_id': email_id
        }

    def get_name(self) -> str:
        return "mark_as_unread"


class MoveMessageAction(Action):
    def execute(self, email_id: str, gmail_client: Any, **kwargs) -> Dict:
        label = kwargs.get('label', 'INBOX')
        success = gmail_client.move_to_label(email_id, label)
        return {
            'action': 'move_message',
            'success': success,
            'email_id': email_id,
            'label': label
        }

    def get_name(self) -> str:
        return "move_message"