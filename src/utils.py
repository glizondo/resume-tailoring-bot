import asyncio
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

from src import handlers

user_timers = {}
time_out_session = 60


def activity_tracker(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        await reset_user_timer(user_id, update, context)
        return await func(update, context, *args, **kwargs)

    return wrapper


async def reset_user_timer(user_id, update, context):
    if user_id in user_timers:
        user_timers[user_id].cancel()

    user_timers[user_id] = asyncio.create_task(run_timer(time_out_session, user_id, update, context))


async def run_timer(delay, user_id, update, context):
    await asyncio.sleep(delay)
    await stop_user_session(user_id, update, context)


async def stop_user_session(user_id, update, context):
    if user_id in user_timers:
        del user_timers[user_id]
    await handlers.stop(update, context)


def cancel(update, context):
    if update.effective_user.id in user_timers:
        user_timers[update.effective_user.id].cancel()
        del user_timers[update.effective_user.id]
    context.user_data.clear()
    context.chat_data.clear()
    return "Cancelled by the user. Run /help command to see your options."
