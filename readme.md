# Gmail Rule Processor

A production-grade, modular Python application that integrates with Gmail API to fetch emails and process them based on configurable JSON rules. Built with extensibility and maintainability in mind using design patterns like Factory, Strategy, and Repository.

## Features

- **Gmail API Integration** - OAuth authentication and email operations
- **SQLite Database** - Auto-creates database and tables on first run
- **Extensible Rule Engine** - Add new conditions and actions without modifying core code
- **JSON-based Configuration** - Define rules in simple JSON format
- **Comprehensive Logging** - Track all rule executions in database
- **Production-Ready** - Error handling, database indexes, and unit tests included

## Quick Start

### Prerequisites

- Python 3.8+
- Gmail account
- Google Cloud Project with Gmail API enabled

### Installation

1. **Clone the repository**
```bash
git clone git@github.com:pwnchaurasia/happyfox_gmail_api.git
cd happyfox
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up Gmail API credentials**

   a. Go to [Google Cloud Console](https://console.cloud.google.com/)
   b. Create a new project or select existing one
   c. Enable Gmail API
   d. Create OAuth 2.0 credentials:
      - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
      - Application type: **Desktop app**
      - Download JSON and save as `credentials.json` in project root
   
   e. Configure OAuth consent screen:
      - User Type: External
      - Add yourself as a test user
      - Scopes: Gmail API

4. **Run the application**
```bash
# Fetch emails (database auto-creates on first run)
cd src
python src/fetch_emails.py --max-results 300

# Process rules
python src/process_rules.py --rules-file rules.json
```

On first run, a browser window will open for Gmail authentication. After authorization, `token.json` will be created automatically.

## Rule Configuration

Rules are defined in `src/rules.json`. Each rule has:
- **name**: Rule identifier
- **description**: What the rule does
- **predicate**: "all" (AND) or "any" (OR)
- **conditions**: Array of conditions to check
- **actions**: Array of actions to perform

### Example Rule
```json
{
  "name": "Interview Emails",
  "description": "Mark interview emails as read",
  "predicate": "all",
  "conditions": [
    {
      "field": "from",
      "predicate": "contains",
      "value": "company.com"
    },
    {
      "field": "subject",
      "predicate": "contains",
      "value": "Interview"
    },
    {
      "field": "date_received",
      "predicate": "less_than_days",
      "value": "7"
    }
  ],
  "actions": [
    {
      "action": "mark_as_read",
      "params": {}
    }
  ]
}
```

### Available Fields

- `from` - Email sender address
- `to` - Email recipient addresses
- `subject` - Email subject line
- `message` - Email body content
- `date_received` - Date email was received

### Available Predicates (Conditions)

**String Predicates:**
- `contains` - Field contains value (case-insensitive)
- `does_not_contain` - Field does not contain value
- `equals` - Field exactly equals value
- `does_not_equal` - Field does not equal value

**Date Predicates:**
- `less_than_days` - Email received less than N days ago
- `greater_than_days` - Email received more than N days ago
- `less_than_months` - Email received less than N months ago
- `greater_than_months` - Email received more than N months ago

### Available Actions

- `mark_as_read` - Mark email as read
- `mark_as_unread` - Mark email as unread
- `move_message` - Move email to a label/folder
```json
  {
    "action": "move_message",
    "params": {
      "label": "Important"
    }
  }
```

### Rule Examples

**Mark all promotional emails as read:**
```json
{
  "name": "Promotions",
  "predicate": "any",
  "conditions": [
    {"field": "subject", "predicate": "contains", "value": "sale"},
    {"field": "subject", "predicate": "contains", "value": "discount"},
    {"field": "subject", "predicate": "contains", "value": "offer"}
  ],
  "actions": [
    {"action": "mark_as_read", "params": {}}
  ]
}
```

**Archive old unread emails:**
```json
{
  "name": "Archive Old",
  "predicate": "all",
  "conditions": [
    {"field": "date_received", "predicate": "greater_than_days", "value": "30"}
  ],
  "actions": [
    {"action": "mark_as_read", "params": {}}
  ]
}
```

## Architecture

### Design Patterns

1. **Factory Pattern** - Dynamic creation of predicates and actions
2. **Strategy Pattern** - Different evaluation strategies for conditions
3. **Repository Pattern** - Clean data access layer
4. **Template Method** - Base classes for predicates and actions

### Why This Architecture?

- **Extensible**: Add new predicates/actions without modifying core code
- **Testable**: Each component can be tested independently
- **Maintainable**: Clear separation of concerns
- **Scalable**: Easy to add features like scheduling, webhooks, etc.

### How It Works
```
1. Fetch emails from Gmail API
2. Store in SQLite database
3. Load rules from JSON
4. For each email:
   - Evaluate conditions using predicates
   - If conditions match, execute actions
   - Log execution in database
```

## Extending the System

### Adding a New Predicate

1. Create predicate class in `src/predicates/`:
```python
from predicates.base import Predicate

class StartsWithPredicate(Predicate):
    def evaluate(self, field_value, rule_value):
        if field_value is None:
            return False
        return str(field_value).lower().startswith(str(rule_value).lower())
    
    def get_name(self):
        return "starts_with"
```

2. Register in `src/predicates/factory.py`:
```python
from predicates.your_file import StartsWithPredicate

PredicateFactory.register(StartsWithPredicate)
```

3. Use in `rules.json`:
```json
{
  "field": "subject",
  "predicate": "starts_with",
  "value": "URGENT"
}
```

### Adding a New Action

1. Create action class in `src/actions/`:
```python
from actions.base import Action

class StarEmailAction(Action):
    def execute(self, email_id, gmail_client, **kwargs):
        try:
            gmail_client.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'addLabelIds': ['STARRED']}
            ).execute()
            return {'action': 'star_email', 'success': True}
        except Exception as e:
            return {'action': 'star_email', 'success': False, 'error': str(e)}
    
    def get_name(self):
        return "star_email"
```

2. Register in `src/actions/factory.py`:

```python
    from actions.your_file import StarEmailAction
    ActionFactory.register(StarEmailAction)
```

3. Use in `rules.json`:
    ```json
    {
    "action": "star_email",
    "params": {}
    }
    ```


## Command Line Options

### fetch_emails.py
```bash
python fetch_emails.py [OPTIONS]

Options:
  --max-results INTEGER  Maximum number of emails to fetch (default: 100)
  --query TEXT          Gmail search query (e.g., "is:unread")
```

Examples:
```bash
# Fetch latest 50 emails
python fetch_emails.py --max-results 50

# Fetch only unread emails
python fetch_emails.py --query "is:unread"

# Fetch emails from specific sender
python fetch_emails.py --query "from:example@company.com"
```

## 🐛 Troubleshooting

### Authentication Issues

**Error: "credentials.json not found"**
- Download OAuth credentials from Google Cloud Console
- Save as `credentials.json` in project root

**Error: "access_denied"**
- Add yourself as a test user in OAuth consent screen
- Make sure Gmail API is enabled

**Browser doesn't open for authentication**
- Delete `token.json` and try again
- Check firewall settings

### Rule Not Working

1. Check rule syntax in `rules.json`
2. Verify field names and predicate names are correct
3. Check `rule_execution_logs` table for errors:
```sql
SELECT * FROM rule_execution_logs WHERE execution_status = 'error';
```
4. Use `--dry-run` to debug without executing actions

### Database Issues

**Database locked error**
- Close any other connections to the database
- Make sure only one script is running at a time

**Tables not created**
- They auto-create on first run
- If issues persist, delete `gmail_rules.db` and run again

## 📚 Key Concepts for Interview

### Why Factory Pattern?

**Problem**: How to create objects dynamically based on JSON configuration?

**Solution**: Factory pattern allows creating predicates/actions by name without if-else chains.
```python
# Without Factory (Bad)
if predicate_name == "contains":
    predicate = ContainsPredicate()
elif predicate_name == "equals":
    predicate = EqualsPredicate()
# ... 50 more if-else statements

# With Factory (Good)
predicate = PredicateFactory.get_predicate(predicate_name)
```

**Benefits:**
- Add new predicates by just registering them
- No need to modify core code
- Very extensible

### Predicates vs Actions

**Predicates** = Conditions that return True/False
- "Does email contain this text?"
- "Is email older than X days?"

**Actions** = Operations that modify emails
- "Mark as read"
- "Move to folder"
- "Forward to someone"

### How to Add New Features

**Interviewer asks: "How would you add email forwarding?"**
```python
# 1. Create action class
class ForwardEmailAction(Action):
    def execute(self, email_id, gmail_client, **kwargs):
        to_address = kwargs.get('to')
        # Forward logic here
        return {'action': 'forward', 'success': True}
    
    def get_name(self):
        return "forward_email"

# 2. Register it
ActionFactory.register(ForwardEmailAction)

```