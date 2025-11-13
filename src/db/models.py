from sqlalchemy import Column, String, DateTime, Text, Integer, JSON, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Email(Base):
    __tablename__ = 'emails'

    id = Column(String(255), primary_key=True)
    thread_id = Column(String(255), index=True)
    from_address = Column(String(500), index=True)
    to_addresses = Column(Text)
    cc_addresses = Column(Text, nullable=True)
    bcc_addresses = Column(Text, nullable=True)
    subject = Column(Text, index=True)
    message_body = Column(Text)
    snippet = Column(Text)
    date_received = Column(DateTime, index=True)
    labels = Column(JSON)
    is_read = Column(Boolean, default=False, index=True)
    is_starred = Column(Boolean, default=False)
    has_attachments = Column(Boolean, default=False)
    raw_headers = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_date_received_desc', date_received.desc()),
        Index('idx_from_date', from_address, date_received),
        Index('idx_subject_date', subject, date_received),
    )

    def __repr__(self):
        return f"<Email(id={self.id}, from={self.from_address}, subject={self.subject[:50]})>"


class RuleExecutionLog(Base):
    __tablename__ = 'rule_execution_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(String(255), index=True)
    rule_name = Column(String(255), index=True)
    rule_conditions = Column(JSON)
    actions_performed = Column(JSON)
    execution_status = Column(String(50))
    error_message = Column(Text, nullable=True)
    executed_at = Column(DateTime, default=func.now(), index=True)

    def __repr__(self):
        return f"<RuleExecutionLog(id={self.id}, email_id={self.email_id}, rule={self.rule_name})>"