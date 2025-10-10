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
        """<text> / reply - Ask @CopilotOfficialBot (supports media in reply)"""
        import asyncio, tempfile, os
        chat = bot_id
        reply = await message.get_reply_message()
        args_text = utils.get_args_raw(message)
        if reply: text = reply.raw_text or args_text or ""
        else: text = args_text or ""
        if not text and not (reply and reply.media):
            await utils.answer(message, "🚫<b>Error! your message is too short.</b>")
            return
        await utils.answer(message, "🤖<b>AI is answering...</b>")
        response = None; response1 = None
        async with message.client.conversation(bot) as conv:
            try:
                if reply and reply.media:
                    caption = text if text else None
                    try: response = await message.client.send_file(bot, file=reply.media, caption=caption)
                    except Exception:
                        tmpf = tempfile.NamedTemporaryFile(delete=False); tmp_path = tmpf.name; tmpf.close()
                        await message.client.download_media(reply, file=tmp_path)
                        response = await message.client.send_file(bot, tmp_path, caption=caption)
                        try: os.remove(tmp_path)
                        except Exception: pass
                else: response = await conv.send_message(text)
                try:
                    response1 = await conv.wait_event(events.NewMessage(incoming=True, from_users=chat), timeout=30)
                except asyncio.TimeoutError:
                    await utils.answer(message, "⚠️ <b>No response from Copilot (timeout).</b>")
                    try: 
                        if response: await response.delete()
                    except Exception: pass
                    return
                answer_text = getattr(response1, "text", None) or getattr(response1, "message", "") or ""
                await utils.answer(message, f"❓<b>Question:</b>\n{text}\n\n🤖 <b>Copilot answer:</b>\n{answer_text}")
            except Exception as e:
                await utils.answer(message, f"⚠️ <b>Error:</b> {e}")
            finally:
                async def _safe_delete(msg):
                    try:
                        if not msg: return
                        if isinstance(msg, (list, tuple)):
                            for m in msg:
                                try: await m.delete()
                                except Exception: pass
                        else:
                            try: await msg.delete()
                            except Exception: pass
                    except Exception: pass
                await _safe_delete(response)
                await _safe_delete(response1)
