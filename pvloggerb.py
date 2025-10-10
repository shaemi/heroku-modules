# meta developer: @hikarimods (edited by Gemini for this request)
# scope: hikka_only
# meta pic: https://img.icons8.com/neon/96/bot.png

import logging
import io
from .. import loader, utils
from ..database import Database
from hikkatl.tl.types import Message
from hikkatl.utils import get_display_name

logger = logging.getLogger(__name__)

# نام کلاس تغییر کرد
@loader.tds
class PVLoggerBotMod(loader.Module):
    """Logs all incoming private messages to a specific channel via an inline bot."""

    strings = {
        # نام داخلی ماژول برای دیتابیس و کانفیگ تغییر کرد
        "name": "PVLoggerBot",
        "log_channel_not_set": (
            "<b>❌ Channel ID not set.</b>\n"
            "Please set <code>log_channel_id</code> in the config first using:\n"
            # نام کانفیگ در پیام خطا آپدیت شد
            "<code>.config PVLoggerBot log_channel_id YOUR_CHANNEL_ID</code>"
        ),
        "logging_status": (
            "<b>🤖 PV Bot-Logger is now {}</b>"
        ),
        "on": "ON",
        "off": "OFF",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "log_channel_id",
                0,
                "Numeric ID of the channel where PV messages will be forwarded.",
                validator=loader.validators.Integer(),
            ),
        )
        self.db = Database(self)

    # نام دستور و آلیاس‌ها تغییر کرد
    @loader.command(aliases=["pvlogbot"])
    async def pvloggerbot(self, message: Message):
        """Enable or disable logging of incoming PV messages via bot."""
        if self.config["log_channel_id"] == 0:
            await utils.answer(message, self.strings("log_channel_not_set"))
            return

        is_enabled = self.db.get(self.strings["name"], "logging_enabled", False)
        
        new_state = not is_enabled
        self.db.set(self.strings["name"], "logging_enabled", new_state)

        status = self.strings("on") if new_state else self.strings("off")
        await utils.answer(message, self.strings("logging_status").format(status))

    @loader.watcher("in", only_messages=True)
    async def watcher(self, message: Message):
        """Watches for incoming messages and sends them via bot if conditions are met."""
        if not self.db.get(self.strings["name"], "logging_enabled", False):
            return

        if self.config["log_channel_id"] == 0:
            return

        if not message.is_private or message.out:
            return
        
        if not hasattr(message, "sender_id") or message.sender_id == self._client.tg_id:
            return

        try:
            sender = await message.get_sender()
            sender_name = utils.escape_html(get_display_name(sender))
            sender_url = utils.get_entity_url(sender)

            caption = f'<b><a href="{sender_url}">{sender_name}</a></b>'
            if message.text:
                caption += f"\n\n{utils.escape_html(message.text)}"

            if message.media and message.file:
                media_file = io.BytesIO(await message.download_media(bytes))
                media_file.name = message.file.name or "file"

                if message.photo:
                    await self.inline.bot.send_photo(self.config["log_channel_id"], media_file, caption=caption)
                elif message.video:
                    await self.inline.bot.send_video(self.config["log_channel_id"], media_file, caption=caption)
                elif message.voice:
                    await self.inline.bot.send_voice(self.config["log_channel_id"], media_file, caption=caption)
                elif message.sticker:
                    await self.inline.bot.send_sticker(self.config["log_channel_id"], media_file)
                    await self.inline.bot.send_message(self.config["log_channel_id"], caption)
                else:
                    await self.inline.bot.send_document(self.config["log_channel_id"], media_file, caption=caption)
            else:
                await self.inline.bot.send_message(
                    self.config["log_channel_id"],
                    caption,
                    disable_web_page_preview=True
                )

        except Exception:
            logger.exception("[PVLoggerBot] Failed to send message via bot. Disabling to prevent spam.")
            self.db.set(self.strings["name"], "logging_enabled", False)
            await self.client.send_message(
                "me",
                "<b>[PVLoggerBot]</b> An error occurred while sending a message via bot. "
                "Logging has been automatically disabled."
            )
