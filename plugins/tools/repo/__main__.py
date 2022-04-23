""" see repo """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import userge, Message, versions

from . import UPSTREAM_REPO


@userge.on_cmd("heartless", about={'header': "get userbot details"})
async def see_repo(message: Message):
    """see repo"""
    output = f"""
• **UserBot Version** : `{get_version()}`
    await message.edit(output)
