from db.models import Email
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session


class EmailRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def save_email(self, email_data: dict) -> Email:
        existing_email = self.db_session.query(Email).filter_by(id=email_data['id']).first()

        if existing_email:
            for key, value in email_data.items():
                if hasattr(existing_email, key):
                    setattr(existing_email, key, value)
            existing_email.updated_at = datetime.now()
            self.db_session.commit()
            return existing_email
        else:
            email = Email(**email_data)
            self.db_session.add(email)
            self.db_session.commit()
            return email

    def save_emails_batch(self, emails_data: List[dict]) -> List[Email]:
        emails = []
        for email_data in emails_data:
            email = self.save_email(email_data)
            emails.append(email)
        return emails

    def get_email_by_id(self, email_id: str) -> Optional[Email]:
        return self.db_session.query(Email).filter_by(id=email_id).first()

    def get_all_emails(self) -> List[Email]:
        return self.db_session.query(Email).all()

    def get_unread_emails(self) -> List[Email]:
        return self.db_session.query(Email).filter_by(is_read=False).all()

    def get_emails_by_sender(self, sender: str) -> List[Email]:
        return self.db_session.query(Email).filter(
            Email.from_address.ilike(f'%{sender}%')
        ).all()

    def get_emails_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Email]:
        return self.db_session.query(Email).filter(
            Email.date_received.between(start_date, end_date)
        ).all()