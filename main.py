import discord
import logging
from discord import app_commands
from enum import Enum
from config import load_config
import sqlite3

import percepteur as pc
import metier as mt
import dofus_const

# Connect to the database
connection_obj = sqlite3.connect('lbg.db')
cursor_obj = connection_obj.cursor()

# Enable foreign key constraints
cursor_obj.execute("PRAGMA foreign_keys = ON;")

# Define table creation statements
tables = [
    """
    CREATE TABLE IF NOT EXISTS METIERS (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Pseudo TEXT NOT NULL,
        Metier TEXT NOT NULL,
        Level INTEGER NOT NULL,
        DateUpdated TEXT,
        DateCreated TEXT,
        UNIQUE(Pseudo, Metier)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS ZONES (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Zone TEXT NOT NULL UNIQUE,
        IsLocked INTEGER NOT NULL DEFAULT 0,
        Date TEXT,
        CreatedBy TEXT,
        UNIQUE(Zone)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Lock (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ZONE TEXT NOT NULL,
        Pseudo TEXT NOT NULL,
        Date TEXT,
        CreatedBy TEXT,
        FOREIGN KEY (ZONE) REFERENCES ZONES (ZONE) ON DELETE CASCADE ON UPDATE CASCADE
    );
    """
]

# Execute table creation
for table in tables:
    cursor_obj.execute(table)

# Commit and close database connection
connection_obj.commit()
connection_obj.close()

# Load configuration
cfg = load_config()
MY_GUILD = discord.Object(id=cfg["guild"])  # Guild ID is required

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
discord_logger = logging.getLogger("discord")


# Enums for actions
class PercepteurAction(Enum):
    register = "register"
    delete = "delete"
    reserve = "reserve"
    next = "next"
    free = "free"
    list_zone = "list_zone"
    list_all_zones = "list_all_zones"


class MetierAction(Enum):
    add = "add"
    delete = "delete"
    update = "update"
    list = "list"


# Custom client class
class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


# Initialize bot
intents = discord.Intents.default()
intents.guilds = True
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f"{client.user} is connected to the following guilds:")
    for guild in client.guilds:
        print(f"- {guild.name} (id: {guild.id})")


# Command: Help
@client.tree.command(name="help", description="Displays the help menu")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="Assistant LBG", description="Available commands:", color=0x3498db)
    embed.add_field(name="/percepteur", value="Percepteur action menu", inline=False)
    embed.add_field(name="/metier", value="Metier action menu", inline=False)
    embed.set_footer(text="A+")
    await interaction.response.send_message(embed=embed)


# Command: Percepteur
@client.tree.command(name="percepteur", description="Manage percepteur actions")
@app_commands.choices(
    percepteur_action=[
        app_commands.Choice(name="Help", value="help"),
        app_commands.Choice(name="Register", value="register"),
        app_commands.Choice(name="Delete", value="delete"),
        app_commands.Choice(name="Reserve", value="reserve"),
        app_commands.Choice(name="Next", value="next"),
        app_commands.Choice(name="Free", value="free"),
        app_commands.Choice(name="List Zone Rows", value="list_zone"),
        app_commands.Choice(name="List All Zones", value="list_all_zones"),
    ],
)
async def percepteur_menu(interaction: discord.Interaction, percepteur_action: app_commands.Choice[str],
                          zone: str = None):
    user = interaction.user.display_name

    func_map = {
        # "help": pc.help(),
        "register": pc.register_zone,
        "delete": pc.delete_zone,
        "reserve": pc.reserve_zone,
        # "next": pc.next_zone(),
        "free": pc.free_zone,
        "list_zone": pc.list_zone,
        "list_all_zones": pc.list_all_zone,
    }

    if percepteur_action.value == "register":
        try:
            func_map[percepteur_action.value](zone, user)
            await interaction.response.send_message(f"Zone '{zone}' registered successfully.")
        except Exception as e:
            await interaction.response.send_message(f"Error registering zone '{zone}': {e}")

    elif percepteur_action.value == "delete":
        if not zone:
            await interaction.response.send_message("Specify a zone to delete.")
            return

        try:
            success = func_map[percepteur_action.value]()
            if success:
                await interaction.response.send_message(f"Zone '{zone}' deleted successfully.")
            else:
                await interaction.response.send_message(f"Zone '{zone}' not found.")
        except Exception as e:
            await interaction.response.send_message(f"Error deleting zone '{zone}': {e}")

    elif percepteur_action.value == "reserve":
        if not zone:
            await interaction.response.send_message("Specify a zone to reserve.")
            return

        try:
            pc.func_map[percepteur_action.value]()
            await interaction.response.send_message(f"Zone '{zone}' reserved successfully.")
        except Exception as e:
            await interaction.response.send_message(f"Error reserving zone '{zone}': {e}")

    elif percepteur_action.value == "free":
        if not zone:
            await interaction.response.send_message("Specify a zone to free.")
            return

        try:
            func_map[percepteur_action.value]()
            await interaction.response.send_message(f"Zone '{zone}' freed successfully.")
        except Exception as e:
            await interaction.response.send_message(f"Error freeing zone '{zone}': {e}")

    elif percepteur_action.value == "list_zone":
        if not zone:
            await interaction.response.send_message("Specify a zone to list rows.")
            return
        rows = func_map[percepteur_action.value]()
        if rows:
            embed = discord.Embed(title=f"Rows for Zone: {zone}", color=0x3498db)
            for row in rows:
                embed.add_field(name=f"Row ID: {row[0]}", value=f"Created By: {row[4]}", inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"No rows found for zone '{zone}'.")

    elif percepteur_action.value == "list_all_zones":
        zones = func_map[percepteur_action.value]()
        if zones:
            embed = discord.Embed(title="All Zones", color=0x3498db)
            for zone in zones:
                embed.add_field(name=f"Zone: {zone[1]}", value=f"Locked: {zone[2]}", inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No zones found.")

    else:
        await interaction.response.send_message("Invalid action.")


# Command: Metier
@client.tree.command(name="metier", description="Manage metier actions")
@app_commands.choices(
    metier_action=[
        app_commands.Choice(name="Register", value="register"),
        app_commands.Choice(name="Delete", value="delete"),
        app_commands.Choice(name="Update", value="update"),
        app_commands.Choice(name="list_artisans", value="list_artisans"),
        app_commands.Choice(name="get_artisan", value="get_artisan"),
    ],
    metier=[app_commands.Choice(name=_conts_metier, value=_conts_metier) for _conts_metier in dofus_const.METIERS],
    # Adding the job choices

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


# Error Handling
@client.tree.error
async def on_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    logging.error(f"Error occurred: {error}")
    await interaction.response.send_message(f"Error: {str(error)}", ephemeral=True)


# Run the bot
client.run(cfg["token"])
