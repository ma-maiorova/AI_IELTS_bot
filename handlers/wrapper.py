from contextvars import Context
from functools import wraps

from telegram import Update

from data import registered_users
from state import UserState


def ensure_registered(func):
    @wraps(func)
    async def wrapper(update: Update, context: Context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in registered_users:
            registered_users[user_id] = {
                "status": "registered",
                "task_type": None,
                "state": UserState.CHOOSING_TOPIC,
                "current_part": 0,
                "current_part_len": 0,
                "current_task": None,
            }
        return await func(update, context, *args, **kwargs)

    return wrapper
