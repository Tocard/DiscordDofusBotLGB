import discord
from discord import app_commands

from commands.utils.admin import is_user_in_list
import commands.utils.percepteur as pc

def admin_wrapper(client):
    @client.tree.command(name="admin", description="Manage admin actions")
    @app_commands.describe(
        actions="Choose an action to perform (e.g., Register, Delete, Update, etc.)",
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
    )
    async def admin_menu(interaction: discord.Interaction, actions: app_commands.Choice[str], pseudo: str = None,  channel_id: str = None):
        user = interaction.user
        if not is_user_in_list(user):
            await interaction.response.send_message('Not admin')

        if actions.value == 'bulk_zone':
            channel = client.get_channel(int(channel_id))
            rows = pc.bulk_zone_from_forum(channel)
            await interaction.response.send_message(rows)
        else:
            await interaction.response.send_message("Bad Action")
