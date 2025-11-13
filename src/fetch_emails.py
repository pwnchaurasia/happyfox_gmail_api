import sys
from dotenv import load_dotenv
load_dotenv('../.env')
import argparse
from db.database import DatabaseManager
from gmail_client import GmailClient
from email_repository import EmailRepository


def main():
    parser = argparse.ArgumentParser(description='Fetch emails from Gmail and store in database')
    parser.add_argument('--max-results', type=int, default=100, help='Maximum number of emails to fetch')
    parser.add_argument('--query', type=str, default='', help='Gmail search query')
    parser.add_argument('--create-tables', action='store_true', help='Create database tables if they don\'t exist')

    args = parser.parse_args()

    try:
        print("Initializing database connection...")
        db_manager = DatabaseManager()

        if args.create_tables:
            print("Creating database tables...")
            db_manager.create_tables()
            print("Tables created successfully!")

        session = db_manager.get_session()
        email_repo = EmailRepository(session)

        print("Authenticating with Gmail API...")
        gmail_client = GmailClient()

        print(f"Fetching emails (max: {args.max_results})...")
        emails_data = gmail_client.fetch_emails(max_results=args.max_results, query=args.query)

        print(f"Found {len(emails_data)} emails. Saving to database...")
        saved_emails = email_repo.save_emails_batch(emails_data)

        print(f"Successfully saved {len(saved_emails)} emails to database!")

        print("\nEmail Statistics:")
        print(f"  Total emails in DB: {len(email_repo.get_all_emails())}")
        print(f"  Unread emails: {len(email_repo.get_unread_emails())}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if 'db_manager' in locals():
            db_manager.close_session()


if __name__ == '__main__':
    main()