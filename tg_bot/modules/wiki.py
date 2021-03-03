from typing import Optional, List
from telegram import Update
from telegram.ext import CallbackContext
from tg_bot import dispatcher
from tg_bot.modules.disable import DisableAbleCommandHandler
import wikipedia


def wiki(update: Update, context: CallbackContext):
    args = context.args
    reply = " ".join(args)
    summary = '{} {}'
    update.message.reply_text(
        summary.format(
            wikipedia.summary(
                reply,
                sentences=3),
            wikipedia.page(reply).url))
            
from tg_bot.modules.language import gs


def get_help(chat):
    return gs(chat, "wikipedia_help")


__mod_name__ = "Wikipedia"  

WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki, pass_args=True)

dispatcher.add_handler(WIKI_HANDLER)
