""" speedtest """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os

import speedtest
import wget

from userge import userge, Message, pool
from userge.utils import humanbytes

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd("speedtest", about={'header': "test your server speed"})
async def speedtst(message: Message):
    await message.edit("`Running speed test . . .`")
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        await message.try_to_edit("`Performing download test . . .`")
        test.download()
        await message.try_to_edit("`Performing upload test . . .`")
        test.upload()
        result = test.results.dict()
    except Exception as e:
        await message.err(e)
        return
    path = await pool.run_in_thread(wget.download)(result['share'])
    output = f"""**ⲋⲧⲁʀⲧⲉⲇ ⲁⲧ ~ {result['timestamp']}--
ⲓⲋⲣ : `{result['client']['isp']}`
ⲥⲟυⲛⲧʀⲩ : `{result['client']['country']}`
ⲛⲁⲙⲉ : `{result['server']['name']}`
ⲥⲟυⲛⲧʀⲩ : `{result['server']['country']}, {result['server']['cc']}`
ⲋⲣⲟⲛⲋⲟʀ : `{result['server']['sponsor']}`
ⳑⲁⲧⲉⲛⲥⲩ : `{result['server']['latency']}`
ⲣⲓⲛⳋ : `{result['ping']}`
ⲋⲉⲛⲧ : `{humanbytes(result['bytes_sent'])}`
ʀⲉⲥⲉⲓⳳⲉⲇ : `{humanbytes(result['bytes_received'])}`
ⲇⲟⲱⲛⳑⲟⲁⲇ : `{humanbytes(result['download'] / 8)}/s`
υⲣⳑⲟⲁⲇ : `{humanbytes(result['upload'] / 8)}/s`**"""
    msg = await message.client.send_photo(chat_id=message.chat.id,
                                          photo=path,
                                          caption=output)
    await CHANNEL.fwd_msg(msg)
    os.remove(path)
    await message.delete()
