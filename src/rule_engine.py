from typing import List, Dict, Any
from predicates.factory import PredicateFactory
from actions.factory import ActionFactory
from db.models import Email, RuleExecutionLog
from datetime import datetime
import json
from pathlib import Path



class RuleEngine:
    def __init__(self, gmail_client, db_session):
        self.gmail_client = gmail_client
        self.db_session = db_session
        self.field_mapping = {
            'from': 'from_address',
            'to': 'to_addresses',
            'subject': 'subject',
            'message': 'message_body',
            'date_received': 'date_received',
            'snippet': 'snippet'
        }

    def load_rules_from_file(self, rules_file: str) -> List[Dict]:
        try:
            src = Path(__file__).parent
            path = src / rules_file
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print("Error loading file", e)

    def process_rules(self, rules: List[Dict], emails: List[Email] = None):
        if emails is None:
            emails = self.db_session.query(Email).all()

        for email in emails:
            for rule in rules:
                self._process_single_rule(rule, email)

    def _process_single_rule(self, rule: Dict, email: Email):
        rule_name = rule.get('name', 'Unnamed Rule')
        conditions = rule.get('conditions', [])
        predicate_type = rule.get('predicate', 'all').lower()
        actions = rule.get('actions', [])

        try:
            if self._evaluate_conditions(conditions, predicate_type, email):
                action_results = self._execute_actions(actions, email.id)
                self._log_execution(
                    email.id,
                    rule_name,
                    conditions,
                    action_results,
                    'success'
                )

        except Exception as e:
            self._log_execution(
                email.id,
                rule_name,
                conditions,
                [],
                'error',
                str(e)
            )

    def _evaluate_conditions(self, conditions: List[Dict], predicate_type: str, email: Email) -> bool:
        if not conditions:
            return False

        results = []

        for condition in conditions:

            field_name = condition.get('field', '').lower()
            predicate_name = condition.get('predicate', '')
            value = condition.get('value', '')

            db_field_name = self.field_mapping.get(field_name)
            if not db_field_name:
                continue

            field_value = getattr(email, db_field_name, None)

            try:
                predicate = PredicateFactory.get_predicate(predicate_name)
                result = predicate.evaluate(field_value, value)
                results.append(result)
            except ValueError as e:
                print(f"Error evaluating predicate {predicate_name}: {e}")
                results.append(False)

        if predicate_type == 'all':
            return all(results) if results else False
        elif predicate_type == 'any':
            return any(results) if results else False
        else:
            return False

    def _execute_actions(self, actions: List[Dict], email_id: str) -> List[Dict]:
        results = []

        for action_config in actions:
            action_name = action_config.get('action', '')
            action_params = action_config.get('params', {})

            try:
                action = ActionFactory.get_action(action_name)
                result = action.execute(email_id, self.gmail_client, **action_params)
                results.append(result)
                self._update_email_state(email_id, action_name, action_params)

            except ValueError as e:
                print(f"Error executing action {action_name}: {e}")
                results.append({
                    'action': action_name,
                    'success': False,
                    'error': str(e)
                })

        return results

    def _update_email_state(self, email_id: str, action_name: str, params: Dict):
        email = self.db_session.query(Email).filter_by(id=email_id).first()
        if not email:
            return

        if action_name == 'mark_as_read':
            email.is_read = True
        elif action_name == 'mark_as_unread':
            email.is_read = False

        email.updated_at = datetime.now()
        self.db_session.commit()

    def _log_execution(self, email_id: str, rule_name: str, conditions: List[Dict],
                       actions: List[Dict], status: str, error_message: str = None):
        log = RuleExecutionLog(
            email_id=email_id,
            rule_name=rule_name,
            rule_conditions=conditions,
            actions_performed=actions,
            execution_status=status,
            error_message=error_message
        )
        self.db_session.add(log)
        self.db_session.commit()