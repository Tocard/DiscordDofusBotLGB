import discord
import logging
from discord import app_commands

import admin
from config import load_config

import percepteur as pc
import metier as mt
import dofus_const

from sql import run_init_sql

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
    print(f"{client.user} is connected to the following guilds:")

    for guild in client.guilds:
        print(f"- {guild.name} (id: {guild.id})")
        print("  Channels and permissions:")

        for channel in guild.channels:
            permissions = channel.permissions_for(guild.me)
            readable_permissions = {
                perm: value for perm, value in permissions if value
            }

            print(f"    - {channel.name} (id: {channel.id}, type: {channel.type})")
            print(f"      Granted Permissions: {list(readable_permissions.keys())}")

    print("Permission listing complete.")


# Command: Help
@client.tree.command(name="help", description="Displays the help menu")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="Assistant LBG", description="Available commands:", color=0x3498db)
    embed.add_field(name="/percepteur", value="Percepteur action menu", inline=False)
    embed.add_field(name="/metier", value="Metier action menu", inline=False)
    embed.add_field(name="/admin", value="Admin action menu", inline=False)
    embed.set_footer(text="A+")
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="perceteur", description="Manage percepteur actions")
@app_commands.describe(
    zone="Where you want to manage percepteur",
)
@app_commands.choices(
    actions=[
        app_commands.Choice(name="Reserve", value="reserve"),
        app_commands.Choice(name="Pose", value="pose"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="Unreserved", value="unreserved"),

    ],
    zone=[app_commands.Choice(name=_zone, value=_zone) for _zone in pc.get_all_zones_name()]
)
async def percepteur_menu(interaction: discord.Interaction, actions: app_commands.Choice[str], zone: str = None):
    user = interaction.user.display_name

    func_map = {
        "reserve": pc.reserve_zone,
        #"add_perceteur": pc.next_zone(),
        #"collect_perceteur": pc.free_zone(),

        "free": pc.free_zone,
        "list_zone": pc.list_zone,
        "list_all_zones": pc.list_all_zone,
    }

    embed = None
    if actions.value == 'reserve':
        embed = func_map[actions.value](zone, user)

    if embed is not None:
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Invalid action.")

@client.tree.command(name="metier", description="Manage work actions")
@app_commands.describe(
    metier_action="Choose an action to perform (e.g., Register, Delete, Update, etc.)",
    metier="Specify the work you want to manage.",
    level="Enter the level for the métier (required for Register and Update).",
    pseudo="Enter the name of the artisan (used with Get Artisan).",
)
@app_commands.choices(
    metier_action=[
        app_commands.Choice(name="Register", value="register"),
        app_commands.Choice(name="Delete", value="delete"),
        app_commands.Choice(name="Update", value="update"),
        app_commands.Choice(name="list_artisans", value="list_artisans"),
        app_commands.Choice(name="get_artisan", value="get_artisan"),
    ],
    metier=[app_commands.Choice(name=_conts_metier, value=_conts_metier) for _conts_metier in dofus_const.METIERS],

    pseudo=[app_commands.Choice(name=_pseudo, value=_pseudo) for _pseudo in mt.get_artisan_list()]

)
async def metier_menu(interaction: discord.Interaction, metier_action: app_commands.Choice[str], metier: str = None,
                      level: int = None, pseudo: str = None):
    user = interaction.user.display_name

    func_map = {
        # "help": mt.help,
        "register": mt.register,
        "delete": mt.delete,
        "update": mt.update,
        "list_artisans": mt.list_artisans,
        "get_artisan": mt.list_metiers_by_user,
    }

    embed = None
    if metier_action.value == 'register' or metier_action.value == 'update':
        embed = func_map[metier_action.value](metier, user, level)
    elif metier_action.value == 'delete':
        embed = func_map[metier_action.value](metier, user)
    elif metier_action.value == 'list_artisans':
        embed = func_map[metier_action.value](metier, level)
    elif metier_action.value == 'get_artisan':
        embed = func_map[metier_action.value](pseudo)

    if embed is not None:
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Invalid action.")


@client.tree.command(name="admin", description="Manage admin actions")
@app_commands.describe(
    actions="Choose an action to perform (e.g., Register, Delete, Update, etc.)",
    metier="Specify the work you want to manage.",
    level="Enter the level for the métier (required for Register and Update).",
    pseudo="Enter the name of the artisan (used with Get Artisan).",
)
@app_commands.choices(
    actions=[
        app_commands.Choice(name="Delay", value="delay"),
        app_commands.Choice(name="Force Remove", value="force remove"),
        app_commands.Choice(name="Force add", value="force_add"),
        app_commands.Choice(name="Delete Zone", value="delete_zone"),
        app_commands.Choice(name="Add Zone", value="delete_zone"),
        app_commands.Choice(name="Bulk Forum Zone", value="bulk_zone"),
    ],

    pseudo=[app_commands.Choice(name=_pseudo, value=_pseudo) for _pseudo in mt.get_artisan_list()]

)
async def admin_menu(interaction: discord.Interaction, actions: app_commands.Choice[str], metier: str = None,
                      level: int = None, pseudo: str = None,  channel_id: str = None):
    user = interaction.user
    if not admin.is_user_in_list(user):
        await interaction.response.send_message('Not admin')

    if actions.value == 'bulk_zone':
        channel = client.get_channel(int(channel_id))
        for thread in channel.threads:
            _thread = {"name": thread.name,
                       "tags": []}
            tags = []
            for tag in thread.applied_tags:
                tags.append(tag.name)
            _thread['tags'] = tags
            await interaction.response.send_message(_thread)


@client.tree.error
async def on_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    logging.error(f"Error occurred: {error}")
    await interaction.response.send_message(f"Error: {str(error)}", ephemeral=True)


# Run the bot
client.run(cfg["token"])
