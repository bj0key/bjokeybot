from io import BytesIO

from discord import File

ACCESS_TOKEN = open("resources/token").read()
TIKTOK_URL = "https://api16-normal-useast5.us.tiktokv.com/media/api/text/speech/invoke/"

# load bjokey into memory, to save read cycles
with open("resources/bjokey.png", "rb") as f:
    BJOKEY_DATA = BytesIO(f.read())
BJOKEY_IMAGE = File(BJOKEY_DATA, filename="bjokey.png")
