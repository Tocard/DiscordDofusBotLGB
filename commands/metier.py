import discord
from discord import app_commands

import commands.utils.metier as mt
from commands.utils import dofus_const


def metier_wrapper(client):
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
            "register": mt.register,
            "delete": mt.delete,
            "update": mt.update,
            "list_artisans": mt.list_artisans,
            "get_artisan": mt.list_metiers_by_user,
        }

        embed = None
        if metier_action.value in ['register', 'update']:
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
