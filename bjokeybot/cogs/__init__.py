from bjokeybot.cogs.base import BjokeyCog
from bjokeybot.cogs.fun import FunCog
from bjokeybot.cogs.stats import StatsCog
from bjokeybot.cogs.tts import TTSCog
from bjokeybot.cogs.util import GeneralUtilityCog, MathUtilityCog
from bjokeybot.cogs.chat_admin import ChatAdminCog
from bjokeybot.cogs.dogging import DoggingCog

all_cogs: list[type[BjokeyCog]] = [FunCog, StatsCog, TTSCog, GeneralUtilityCog, MathUtilityCog, ChatAdminCog, DoggingCog]
