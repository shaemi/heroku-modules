# by: aliultraa.t.me
import logging
from .. import loader, utils
from ..database import Database
from hikkatl.tl.types import Message

logger = logging.getLogger(__name__)

@loader.tds
class PVLoggerMod(loader.Module):
    """Logs all incoming private messages to a specific channel."""

    strings = {
        "name": "PVLogger",
        "log_channel_not_set": (
            "<b>❌ Channel ID not set.</b>\n"
            "Please set <code>log_channel_id</code> in the config first using:\n"
            "<code>.config PVLogger log_channel_id YOUR_CHANNEL_ID</code>"
        ),
        "logging_status": (
            "<b>👁️ PV Logging is now {}</b>"
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

    @loader.command(aliases=["pvlog", "logpv"])
    async def pvlogger(self, message: Message):
        """Enable or disable logging of incoming PV messages."""
        if self.config["log_channel_id"] == 0:
            await utils.answer(message, self.strings("log_channel_not_set"))
            return

        is_enabled = self.db.get(self.strings["name"], "logging_enabled", False)
        
        # Toggle the state
        new_state = not is_enabled
        self.db.set(self.strings["name"], "logging_enabled", new_state)

        status = self.strings("on") if new_state else self.strings("off")
        await utils.answer(message, self.strings("logging_status").format(status))

    @loader.watcher("in", only_messages=True)
    async def watcher(self, message: Message):
        """Watches for incoming messages and forwards them if conditions are met."""
        if not self.db.get(self.strings["name"], "logging_enabled", False):
            return

        if self.config["log_channel_id"] == 0:
            return

        if not message.is_private or message.out:
            return
        
        sender = await message.get_sender()

        if sender and sender.bot:
            return

        # Ensure it's not from yourself
        if not hasattr(message, "sender_id") or message.sender_id == self._client.tg_id or message.sender_id == 777000:
            return

        try:
            await self.client.forward_messages(
                self.config["log_channel_id"],
                message
            )
        except Exception:
            try:
                sender_name = utils.escape_html(sender.first_name if sender else "Unknown")
                sender_id = message.sender_id
                
                log_caption = (
                    f"<b>🔒 Protected Message (Copy)</b>\n"
                    f"<b>From:</b> <a href='tg://user?id={sender_id}'>{sender_name}</a>\n"
                    f"➖➖➖➖➖➖➖➖\n"
                    f"{utils.escape_html(message.text or '')}"
                )

                await self.client.send_message(
                    self.config["log_channel_id"],
                    log_caption,
                    file=message.media
                )
            except Exception as e:
                logger.exception(f"[PVLogger] Critical Error: {e}")
