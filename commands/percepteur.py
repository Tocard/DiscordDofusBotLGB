import discord
from discord import app_commands


import commands.utils.percepteur as pc

def percepteur_wrapper(client):
    @client.tree.command(name="percepteur", description="Manage percepteur actions")
    @app_commands.describe(
        zone="Where you want to manage percepteur",
    )
    @app_commands.choices(
        actions=[
            app_commands.Choice(name="Reserve", value="reserve_percepteur"),
            app_commands.Choice(name="Pose", value="add_percepteur"),
            app_commands.Choice(name="remove", value="collect_percepteur"),
            app_commands.Choice(name="Unreserved", value="unreserve_percepteur"),
        ],
    )
    async def percepteur_menu(interaction: discord.Interaction, actions: app_commands.Choice[str], zone: str = None):
        user = interaction.user.display_name
        func_map = {
            "reserve_percepteur": pc.reserve_zone,
            "unreserve_percepteur": pc.unreserve_zone,
            "free": pc.free_zone,
            "list_zone": pc.list_zone,
            "list_all_zones": pc.list_all_zone,
        }

        embed = None
        if actions.value == 'reserve_percepteur':
            embed = func_map[actions.value](zone, user)
        if embed is not None:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Invalid action.")

    @percepteur_menu.autocomplete("zone")
    async def zone_autocomplete(interaction: discord.Interaction, current: str):
        all_zones = pc.get_zones_like(current)
        filtered_zones = [zone for zone in all_zones if zone.lower().startswith(current.lower())]
        return [app_commands.Choice(name=zone, value=zone) for zone in filtered_zones]
