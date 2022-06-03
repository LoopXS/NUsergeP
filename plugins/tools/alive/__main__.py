""" check your userbot is alive """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import os
import re
from typing import Tuple, Optional

import wget
from pyrogram.errors import (
    ChatSendMediaForbidden, Forbidden, SlowmodeWait, PeerIdInvalid,
    FileIdInvalid, FileReferenceEmpty, BadRequest, ChannelInvalid, MediaEmpty
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from userge import userge, Message, pool, config, versions as ver, logging
from userge.utils import get_file_id_of_media, get_custom_import_re
from .. import alive
from ...builtin import sudo, system

antispam = get_custom_import_re("userge.plugins.admin.antispam", False)
pmpermit = get_custom_import_re("userge.plugins.utils.pmpermit", False)

_LOG = logging.getLogger(__name__)

_IS_TELEGRAPH = False
_IS_STICKER = False

_DEFAULT = "https://t.me/UserGeSpam/457297"
_CHAT, _MSG_ID = None, None
_LOGO_ID = None


@userge.on_cmd("alive", about={
    'header': "This command is just for fun"}, allow_channels=False)
async def _alive(message: Message):
    if not (_CHAT and _MSG_ID):
        try:
            _set_data()
        except Exception as set_err:
            _LOG.exception("There was some problem while setting Media Data. "
                           f"trying again... ERROR:: {set_err} ::")
            _set_data(True)

    alive_text, markup = await _get_text_and_markup(message)
    if _MSG_ID == "text_format":
        return await message.edit(alive_text, disable_web_page_preview=True, reply_markup=markup)
    await message.delete()
    try:
        await _send_alive(message, alive_text, markup)
    except (FileIdInvalid, FileReferenceEmpty, BadRequest):
        await _refresh_id(message)
        await _send_alive(message, alive_text, markup)


def _get_mode() -> str:
    if userge.dual_mode:
        return "Dual"
    if config.BOT_TOKEN:
        return "Bot"
    return "User"


async def _get_text_and_markup(message: Message) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
    markup = None
    output = f"""
**✦ ⲏⲉⲁʀⲧⳑⲉⲋⲋ ᥱ᥊ᥴᥣᥙsi᥎ᥱ ⲃⲟⲧ**
≺━━━━━━━━ - ━━━━━━━≻
**✗ υⲣⲧⲓⲙⲉ ➛** `{userge.uptime}`
**✗ ⳳⲉʀⲋⲓⲟⲛ ➛** `1.7`
**✗ ⲙⲟⲇⲉ ➛** `Dual`
≺━━━━━━━━ - ━━━━━━━≻
**✗ ⲋυⲇⲟ ➛** `{_parse_arg(sudo.Dynamic.ENABLED)}`"""
output += f"""
**✗ ⲣⲩⲧⲏⲟⲛ ➛** `{ver.__python_version__}`
**✗ ⲣⲩʀⲟⳋʀⲁⲙ ➛** `{ver.__pyro_version__}`
≺━━━━━━━━ - ━━━━━━━≻
🎭 T.me/DarkPentester**"""
    if not message.client.is_bot:
        outputr = f"""
**✦ ⲏⲉⲁʀⲧⳑⲉⲋⲋ ᥱ᥊ᥴᥣᥙsi᥎ᥱ ⲃⲟⲧ**
≺━━━━━━━━ - ━━━━━━━≻
**✗ υⲣⲧⲓⲙⲉ ➛** `{userge.uptime}`
**✗ ⳳⲉʀⲋⲓⲟⲛ ➛** `1.7`
**✗ ⲙⲟⲇⲉ ➛** `Dual`
≺━━━━━━━━ - ━━━━━━━≻
**✗ ⲋυⲇⲟ ➛** `{_parse_arg(sudo.Dynamic.ENABLED)}`
**✗ ⲣⲩⲧⲏⲟⲛ ➛** `{ver.__python_version__}`
**✗ ⲣⲩʀⲟⳋʀⲁⲙ ➛** `{ver.__pyro_version__}`
≺━━━━━━━━ - ━━━━━━━≻
🎭 T.me/DarkPentester**"""
        copy_ = "https://xhamster.com/"
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="• ᴅᴇᴠᴇʟᴏᴘᴇʀ •", url="https://t.me/DarkPentester"),
                InlineKeyboardButton(text="• ᴀꜱꜱɪꜱᴛᴀɴᴛ •", url="DarkPentesterBot")
            ],
            [InlineKeyboardButton(text="• ʀᴇᴘᴏ •", url=copy_)]
        ])
    return outputr, markup


def _parse_arg(arg: bool) -> str:
    return "enabled" if arg else "disabled"


async def _send_alive(message: Message,
                      text: str,
                      reply_markup: Optional[InlineKeyboardMarkup],
                      recurs_count: int = 0) -> None:
    if not _LOGO_ID:
        await _refresh_id(message)
    should_mark = None if _IS_STICKER else reply_markup
    if _IS_TELEGRAPH:
        await _send_telegraph(message, text, reply_markup)
    else:
        try:
            await message.client.send_cached_media(chat_id=message.chat.id,
                                                   file_id=_LOGO_ID,
                                                   caption=text,
                                                   reply_markup=should_mark)
            if _IS_STICKER:
                raise ChatSendMediaForbidden
        except SlowmodeWait as s_m:
            await asyncio.sleep(s_m.x)
            text = f'<b>{str(s_m).replace(" is ", " was ")}</b>\n\n{text}'
            return await _send_alive(message, text, reply_markup)
        except MediaEmpty:
            if recurs_count >= 2:
                raise ChatSendMediaForbidden
            await _refresh_id(message)
            return await _send_alive(message, text, reply_markup, recurs_count + 1)
        except (ChatSendMediaForbidden, Forbidden):
            await message.client.send_message(chat_id=message.chat.id,
                                              text=text,
                                              disable_web_page_preview=True,
                                              reply_markup=should_mark)


async def _refresh_id(message: Message) -> None:
    global _LOGO_ID, _IS_STICKER  # pylint: disable=global-statement
    try:
        media = await message.client.get_messages(_CHAT, _MSG_ID)
    except (ChannelInvalid, PeerIdInvalid, ValueError):
        _set_data(True)
        return await _refresh_id(message)
    else:
        if media.sticker:
            _IS_STICKER = True
        _LOGO_ID = get_file_id_of_media(media)


def _set_data(errored: bool = False) -> None:
    global _CHAT, _MSG_ID, _IS_TELEGRAPH  # pylint: disable=global-statement

    pattern_1 = r"^(http(?:s?):\/\/)?(www\.)?(t.me)(\/c\/(\d+)|:?\/(\w+))?\/(\d+)$"
    pattern_2 = r"^https://telegra\.ph/file/\w+\.\w+$"
    if alive.ALIVE_MEDIA and not errored:
        if alive.ALIVE_MEDIA.lower().strip() == "nothing":
            _CHAT = "text_format"
            _MSG_ID = "text_format"
            return
        media_link = alive.ALIVE_MEDIA
        match_1 = re.search(pattern_1, media_link)
        match_2 = re.search(pattern_2, media_link)
        if match_1:
            _MSG_ID = int(match_1.group(7))
            if match_1.group(5):
                _CHAT = int("-100" + match_1.group(5))
            elif match_1.group(6):
                _CHAT = match_1.group(6)
        elif match_2:
            _IS_TELEGRAPH = True
        elif "|" in alive.ALIVE_MEDIA:
            _CHAT, _MSG_ID = alive.ALIVE_MEDIA.split("|", maxsplit=1)
            _CHAT = _CHAT.strip()
            _MSG_ID = int(_MSG_ID.strip())
    else:
        match = re.search(pattern_1, _DEFAULT)
        _CHAT = match.group(6)
        _MSG_ID = int(match.group(7))


async def _send_telegraph(msg: Message, text: str, reply_markup: Optional[InlineKeyboardMarkup]):
    path = os.path.join(config.Dynamic.DOWN_PATH, os.path.split(alive.ALIVE_MEDIA)[1])
    if not os.path.exists(path):
        await pool.run_in_thread(wget.download)(alive.ALIVE_MEDIA, path)
    if path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
        await msg.client.send_photo(
            chat_id=msg.chat.id,
            photo=path,
            caption=text,
            reply_markup=reply_markup
        )
    elif path.lower().endswith((".mkv", ".mp4", ".webm")):
        await msg.client.send_video(
            chat_id=msg.chat.id,
            video=path,
            caption=text,
            reply_markup=reply_markup
        )
    else:
        await msg.client.send_document(
            chat_id=msg.chat.id,
            document=path,
            caption=text,
            reply_markup=reply_markup
        )
