import sys
from dotenv import load_dotenv

from db.models import Email

load_dotenv('../.env')
import argparse
from db.database import DatabaseManager
from gmail_client import GmailClient
from rule_engine import RuleEngine
from email_repository import EmailRepository



def main():
    parser = argparse.ArgumentParser(description='Process emails based on rules')
    parser.add_argument('--rules-file', type=str, default='rules.json', help='Path to rules JSON file')
    parser.add_argument('--email-id', type=str, help='Process specific email by ID')
    parser.add_argument('--dry-run', action='store_true', help='Dry run - don\'t actually execute actions')

    args = parser.parse_args()

    try:
        print("Initializing database connection...")
        db_manager = DatabaseManager()
        session = db_manager.get_session()

        print("Authenticating with Gmail API...")
        gmail_client = GmailClient()

        print(f"Loading rules from {args.rules_file}...")
        rule_engine = RuleEngine(gmail_client, session)
        rules = rule_engine.load_rules_from_file(args.rules_file)

        print(f"Loaded {len(rules)} rules:")
        for i, rule in enumerate(rules, 1):
            print(f"  {i}. {rule.get('name', 'Unnamed')}: {rule.get('description', 'No description')}")

        if args.email_id:
            email_repo = EmailRepository(session)
            email = email_repo.get_email_by_id(args.email_id)
            if not email:
                print(f"Email with ID {args.email_id} not found!")
                sys.exit(1)
            emails = [email]
            print(f"\nProcessing single email: {email.id}")
        else:
            emails = session.query(Email).all()
            print(f"\nProcessing all emails in database...")

        if args.dry_run:
            print("\n*** DRY RUN MODE - No actions will be executed ***\n")

        print("Processing rules...")
        rule_engine.process_rules(rules, emails)

        print("\nRule processing completed!")

    except FileNotFoundError:
        print(f"Error: Rules file '{args.rules_file}' not found!", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'db_manager' in locals():
            db_manager.close_session()


if __name__ == '__main__':
    main()