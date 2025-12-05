# Powered By Team DeadlineTech
from DeadlineTech.core.bot import Anony
from DeadlineTech.core.dir import dirr
from DeadlineTech.core.userbot import Userbot
from DeadlineTech.misc import dbb, heroku

from .logging import LOGGER

dirr()
dbb()
heroku()

app = Anony()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
