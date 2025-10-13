version = (1, 0, 1)

# by: aliultraa.t.me

import random
from datetime import timedelta
from telethon import events
from telethon import functions
from telethon.tl.types import Message
from .. import loader, utils

bot = "@CopilotOfficialBot"
bot_id = 7147619821

@loader.tds
class CopilotAIMod(loader.Module):
    """AI Assist for @CopilotOfficialBot"""

    strings = {
        "name": "CopilotAI",
    }
            	
    @loader.command()
    async def copilotdelcmd(self, message):
        """- Clear chat history."""
        chat = bot_id
        text = "/newchat"
        async with message.client.conversation(bot) as conv:
            response = await conv.send_message(text)
            response1 = await conv.wait_event(events.NewMessage(incoming=True, from_users=chat))
            await utils.answer(message, "✅ <b>History cleared!</b>")
            await response.delete()
            await response1.delete()
           
           
    @loader.command()
    async def aicmd(self, message):
        """- Ask Copilot (supports media & files in reply)"""
        chat = bot_id
        reply = await message.get_reply_message()
        text = utils.get_args_raw(message) or (reply.text if reply else "")
        if not text and not (reply and reply.media):
            return await utils.answer(message, "🚫 <b>Send text or reply to a message.</b>")
        await utils.answer(message, "🤖 <b>AI is answering...</b>")
        async with message.client.conversation(bot) as conv:
            if reply and reply.media:
                sent = await message.client.send_file(bot, reply.media, caption=text or None)
            else:
                sent = await conv.send_message(text)
            response = await conv.wait_event(events.NewMessage(incoming=True, from_users=chat))
            await utils.answer(message, f"❓<b>Q:</b> {text}\n\n🤖 <b>A:</b>\n{response.text}")
            await sent.delete(); await response.delete()
