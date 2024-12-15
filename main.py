import discord
import logging
from discord import app_commands
from enum import Enum
from config import load_config
from datetime import datetime
import sqlite3

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
        Lvl TEXT,
        CreatedBy TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS ZONES (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ZONE TEXT NOT NULL UNIQUE,
        IsLocked INTEGER NOT NULL DEFAULT 0,
        Date TEXT,
        CreatedBy TEXT
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


# Helper: Register Zone
def percepteur_register_zone(zone_name: str, user: str, is_locked: bool = False):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        cursor_obj.execute(
            "INSERT INTO ZONES (ZONE, IsLocked, Date, CreatedBy) VALUES (?, ?, ?, ?);",
            (zone_name, int(is_locked), current_date, user)
        )
        connection_obj.commit()
        print(f"Zone '{zone_name}' registered successfully.")
    except sqlite3.IntegrityError as e:
        print(f"Error registering zone '{zone_name}': {e}")
    finally:
        connection_obj.close()


# Helper: Delete Zone
def percepteur_delete_zone(zone_name: str):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")

    try:
        cursor_obj.execute("DELETE FROM ZONES WHERE ZONE = ?;", (zone_name,))
        changes = connection_obj.total_changes
        connection_obj.commit()
        if changes > 0:
            print(f"Zone '{zone_name}' deleted successfully.")
            return True
        else:
            print(f"Zone '{zone_name}' not found.")
            return False
    finally:
        connection_obj.close()


# Helper: Reserve Zone
def percepteur_reserve_zone(zone_name: str, user: str):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # Insert into Lock table
        cursor_obj.execute(
            "INSERT INTO Lock (ZONE, Pseudo, Date, CreatedBy) VALUES (?, ?, ?, ?);",
            (zone_name, user, current_date, user)
        )

        # Update the IsLocked field in ZONES table
        cursor_obj.execute(
            "UPDATE ZONES SET IsLocked = 1 WHERE ZONE = ?;",
            (zone_name,)
        )

        connection_obj.commit()
        print(f"Zone '{zone_name}' reserved successfully.")
    except sqlite3.IntegrityError as e:
        print(f"Error reserving zone '{zone_name}': {e}")
    finally:
        connection_obj.close()


# Helper: Free Zone
def percepteur_free_zone(zone_name: str):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")

    try:
        # Delete from Lock table
        cursor_obj.execute(
            "DELETE FROM Lock WHERE ZONE = ?;",
            (zone_name,)
        )

        # Update the IsLocked field in ZONES table
        cursor_obj.execute(
            "UPDATE ZONES SET IsLocked = 0 WHERE ZONE = ?;",
            (zone_name,)
        )

        connection_obj.commit()
        print(f"Zone '{zone_name}' freed successfully.")
    except sqlite3.IntegrityError as e:
        print(f"Error freeing zone '{zone_name}': {e}")
    finally:
        connection_obj.close()


# Command: Percepteur
@client.tree.command(name="percepteur", description="Manage percepteur actions")
@app_commands.choices(
    percepteur_action=[
        app_commands.Choice(name="Register", value="register"),
        app_commands.Choice(name="Delete", value="delete"),
        app_commands.Choice(name="Reserve", value="reserve"),
        app_commands.Choice(name="Next", value="next"),
        app_commands.Choice(name="Free", value="free"),
        app_commands.Choice(name="List Zone Rows", value="list_zone"),
        app_commands.Choice(name="List All Zones", value="list_all_zones"),
    ]
)
async def percepteur(interaction: discord.Interaction, percepteur_action: app_commands.Choice[str], zone: str = None):
    user = interaction.user.display_name

    if percepteur_action.value == "register":
        try:
            percepteur_register_zone(zone, user)
            await interaction.response.send_message(f"Zone '{zone}' registered successfully.")
        except Exception as e:
            await interaction.response.send_message(f"Error registering zone '{zone}': {e}")

    elif percepteur_action.value == "delete":
        if not zone:
            await interaction.response.send_message("Specify a zone to delete.")
            return

        try:
            success = percepteur_delete_zone(zone)
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
            percepteur_reserve_zone(zone, user)
            await interaction.response.send_message(f"Zone '{zone}' reserved successfully.")
        except Exception as e:
            await interaction.response.send_message(f"Error reserving zone '{zone}': {e}")

    elif percepteur_action.value == "free":
        if not zone:
            await interaction.response.send_message("Specify a zone to free.")
            return

        try:
            percepteur_free_zone(zone)
            await interaction.response.send_message(f"Zone '{zone}' freed successfully.")
        except Exception as e:
            await interaction.response.send_message(f"Error freeing zone '{zone}': {e}")

    elif percepteur_action.value == "list_zone":
        if not zone:
            await interaction.response.send_message("Specify a zone to list rows.")
            return

        connection_obj = sqlite3.connect('lbg.db')
        cursor_obj = connection_obj.cursor()
        try:
            cursor_obj.execute("SELECT * FROM ZONES WHERE ZONE = ?;", (zone,))
            rows = cursor_obj.fetchall()
            if rows:
                embed = discord.Embed(title=f"Rows for Zone: {zone}", color=0x3498db)
                for row in rows:
                    embed.add_field(name=f"Row ID: {row[0]}", value=f"Created By: {row[4]}", inline=False)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"No rows found for zone '{zone}'.")
        finally:
            connection_obj.close()

    elif percepteur_action.value == "list_all_zones":
        connection_obj = sqlite3.connect('lbg.db')
        cursor_obj = sqlite3.connect('lbg.db')
        cursor_obj = connection_obj.cursor()
        try:
            cursor_obj.execute("SELECT * FROM ZONES;")
            zones = cursor_obj.fetchall()
            if zones:
                embed = discord.Embed(title="All Zones", color=0x3498db)
                for zone in zones:
                    embed.add_field(name=f"Zone: {zone[1]}", value=f"Locked: {zone[2]}", inline=False)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("No zones found.")
        finally:
            connection_obj.close()

    else:
        await interaction.response.send_message("Invalid action.")


# Command: Metier
@client.tree.command(name="metier", description="Manage metier actions")
@app_commands.choices(
    metier_action=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Delete", value="delete"),
        app_commands.Choice(name="Update", value="update"),
        app_commands.Choice(name="List", value="list"),
    ]
)
async def metier(interaction: discord.Interaction, metier_action: app_commands.Choice[str], job: str = None,
                 level: int = None):
    embed = discord.Embed(title="Metier Actions", color=0x2ecc71)
    embed.add_field(name=f"Action: {metier_action.name}", value=f"Job: {job} (Level: {level})", inline=False)
    embed.set_footer(text="Command executed successfully!")
    await interaction.response.send_message(embed=embed)


# Error Handling
@client.tree.error
async def on_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    logging.error(f"Error occurred: {error}")
    await interaction.response.send_message(f"Error: {str(error)}", ephemeral=True)


# Run the bot
client.run(cfg["token"])
