import discord
import logging
from discord import app_commands

from commands.utils.config import load_config
from commands.help import helper_wrapper
from commands.percepteur import percepteur_wrapper
from commands.metier import metier_wrapper
from commands.admin import admin_wrapper
from commands.utils.sql import run_init_sql

run_init_sql()

cfg = load_config()
MY_GUILD = discord.Object(id=cfg["guild"])

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
discord_logger = logging.getLogger("discord")

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

_intents = discord.Intents.default()
_intents.guilds = True
client = MyClient(intents=_intents)

@client.event
async def on_ready():
    logging.info(f"{client.user} is connected to the following guilds:")
    for guild in client.guilds:
        logging.info(f"{guild.name} (id: {guild.id})")
    logging.info("Permission listing complete.")

# Register commands
helper_wrapper(client)
percepteur_wrapper(client)
metier_wrapper(client)
admin_wrapper(client)

# Run the bot
client.run(cfg["token"])
