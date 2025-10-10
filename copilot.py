version = (1, 0, 0)

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
    async def copilotcmd(self, message):
        """<текст> - Ask Copilot"""
        chat = bot_id
        reply = await message.get_reply_message()
        text = reply.raw_text if reply else utils.get_args_raw(message)
        if len(text) < 3:
        	await utils.answer(message, "🚫<b>Ошибка!\nСлишком маленький запрос.</b>")
        	return
        await utils.answer(message, "🤖<b>Нейросеть обрабатывает ваш запрос...</b>")
        async with message.client.conversation(bot) as conv:
            response = await conv.send_message(text)
            response1 = await conv.wait_event(events.NewMessage(incoming=True, from_users=chat))
            await utils.answer(message, f"❓<b>Вопрос:</b> \n{text}\n\n🤖 <b>Ответ нейросети:</b>\n{response1.text}")
            await response.delete()
            await response1.delete()
