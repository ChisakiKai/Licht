import html
from typing import Optional

from telegram import MAX_MESSAGE_LENGTH, Message, ParseMode, User
from telegram.utils.helpers import escape_markdown

import tg_bot.modules.sql.userinfo_sql as sql
from tg_bot import DEV_USERS, dispatcher
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.alternate import typing_action
from tg_bot.modules.helper_funcs.extraction import extract_user


USER_INFO = get_collection("USER_INFO")
USER_BIO = get_collection("USER_BIO")


@typing_action
def about_me(update, context):
    message = update.effective_message  # type: Optional[Message]
    args = context.args
    user_id = extract_user(message, args)

    if user_id:
        user = context.bot.get_chat(user_id)
    else:
        user = message.from_user

    info = USER_INFO.find_one({'_id': user.id})

    if info:
        update.effective_message.reply_text(
            "*{}*:\n{}".format(user.first_name, escape_markdown(info["info"])),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif message.reply_to_message:
        username = message.reply_to_message.from_user.first_name
        update.effective_message.reply_text(
            username + "Information about him is currently unavailable !"
        )
    else:
        update.effective_message.reply_text(
            "You have not added any information about yourself yet !"
        )


@typing_action
def set_about_me(update, context):
    message = update.effective_message  # type: Optional[Message]
    user_id = message.from_user.id
    if user_id == 1087968824:
        message.reply_text(
            "You cannot set your own bio when you're in anonymous admin mode!"
        )
        return

    text = message.text
    info = text.split(
        None, 1
    )  # use python's maxsplit to only remove the cmd, hence keeping newlines.
    if len(info) == 2:
        if len(info[1]) < MAX_MESSAGE_LENGTH // 4:
            USER_INFO.update_one(
                {'_id': user_id},
                {"$set": {'info': info[1]}},
                upsert=True)
            message.reply_text("Your bio has been saved successfully")
        else:
            message.reply_text(
                " About You{} To be confined to letters ".format(
                    MAX_MESSAGE_LENGTH // 4, len(info[1])
                )
            )


@typing_action
def about_bio(update, context):
    message = update.effective_message  # type: Optional[Message]
    args = context.args

    user_id = extract_user(message, args)
    if user_id:
        user = context.bot.get_chat(user_id)
    else:
        user = message.from_user

    info = USER_BIO.find_one({'_id': user.id})

    if info:
        update.effective_message.reply_text(
            "*{}*:\n{}".format(user.first_name, escape_markdown(info["bio"])),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif message.reply_to_message:
        username = user.first_name
        update.effective_message.reply_text(
            "{} No details about him have been saved yet !".format(username)
        )
    else:
        update.effective_message.reply_text(
            " Your bio  about you has been saved !"
        )


@typing_action
def set_about_bio(update, context):
    message = update.effective_message  # type: Optional[Message]
    sender = update.effective_user  # type: Optional[User]
    if message.reply_to_message:
        repl_message = message.reply_to_message
        user_id = repl_message.from_user.id
        if user_id == message.from_user.id:
            message.reply_text(
                "Are you looking to change your own ... ?? That 's it."
            )
            return
        elif user_id == context.bot.id and sender.id not in DEV_USERS:
            message.reply_text("Only DEV USERS can change my information.")
            return
        elif user_id == 1087968824:
            message.reply_text("You cannot set anonymous user bio!")
            return

        text = message.text
        # use python's maxsplit to only remove the cmd, hence keeping newlines.
        bio = text.split(None, 1)
        if len(bio) == 2:
            if len(bio[1]) < MAX_MESSAGE_LENGTH // 4:
                USER_BIO.update_one(
                    {'_id': user_id},
                    {"$set": {'bio': bio[1]}},
                    upsert=True)
                message.reply_text(
                    "{} bio has been successfully saved!".format(
                        repl_message.from_user.first_name
                    )
                )
            else:
                message.reply_text(
                    "About you {} Must stick to the letter! The number of characters you have just tried {} hm .".format(
                        MAX_MESSAGE_LENGTH // 4, len(bio[1])
                    )
                )
    else:
        message.reply_text(
            " His bio can only be saved if someone MESSAGE as a REPLY"
        )


def __user_info__(user_id):
    bdata = USER_BIO.find_one({'_id': user_id})
    if bdata:
        bio = html.escape(bdata["bio"])
    idata = USER_INFO.find_one({'_id': user_id})
    if idata:
        me = html.escape(idata["info"])

    if bdata and idata:
        return "<b>About user:</b>\n{me}\n\n<b>What others say:</b>\n{bio}".format(
            me=me, bio=bio
        )
    elif bdata:
        return "<b>What others say:</b>\n{}\n".format(bio)
    elif idata:
        return "<b>About user:</b>\n{}".format(me)
    else:
        return ""


from tg_bot.modules.language import gs


def get_help(chat):
    return gs(chat, "userinfo_help")


__mod_name__ = "Bios/Abouts"

SET_BIO_HANDLER = DisableAbleCommandHandler(
    "setbio", set_about_bio, run_async=True
)
GET_BIO_HANDLER = DisableAbleCommandHandler(
    "bio", about_bio, pass_args=True, run_async=True
)

SET_ABOUT_HANDLER = DisableAbleCommandHandler(
    "setme", set_about_me, run_async=True
)
GET_ABOUT_HANDLER = DisableAbleCommandHandler(
    "me", about_me, pass_args=True, run_async=True
)

dispatcher.add_handler(SET_BIO_HANDLER)
dispatcher.add_handler(GET_BIO_HANDLER)
dispatcher.add_handler(SET_ABOUT_HANDLER)
dispatcher.add_handler(GET_ABOUT_HANDLER)
