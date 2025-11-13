from actions.base import Action
from actions.email_actions import (
    MarkAsReadAction,
    MarkAsUnreadAction,
    MoveMessageAction
)
from typing import Dict, Type


class ActionFactory:
    _actions: Dict[str, Type[Action]] = {}

    @classmethod
    def register(cls, action_class: Type[Action]):
        action_instance = action_class()
        cls._actions[action_instance.get_name()] = action_class
        return action_class

    @classmethod
    def get_action(cls, action_name: str) -> Action:
        action_class = cls._actions.get(action_name)
        if not action_class:
            raise ValueError(f"Unknown action: {action_name}")
        return action_class()

    @classmethod
    def get_available_actions(cls) -> list:
        return list(cls._actions.keys())


ActionFactory.register(MarkAsReadAction)
ActionFactory.register(MarkAsUnreadAction)
ActionFactory.register(MoveMessageAction)