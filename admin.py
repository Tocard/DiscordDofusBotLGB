import discord
from discord import app_commands
from config import load_config

cfg = load_config()


def is_user_in_list(user: discord.User) -> bool:
    """
    Check if the user's ID is in the predefined list of IDs.

    :param user: The discord.User object to check.
    :return: True if the user's ID is in the list, False otherwise.
    """
    return user.id in cfg['admin_user']