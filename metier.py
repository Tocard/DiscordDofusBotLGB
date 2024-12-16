from datetime import datetime
import sqlite3
import logging
import discord

import color
import bot_default as bf

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def register(metier: str, user: str, level: int):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    embed = bf.error_generic()

    try:
        cursor_obj.execute(
            "INSERT INTO METIERS (Pseudo, Metier, level, DateCreated, DateUpdated) VALUES (?, ?, ?, ?, ?);",
            (user, metier, level, current_date, current_date)
        )
        connection_obj.commit()
        logging.info(f"{user} registered '{metier}:{level}' successfully.")
        embed = discord.Embed(title=f"Métier Enregistré", color=color.GREEN)
        embed.add_field(name=f"Metier: {metier} ", value=f"Lvl: {level}", inline=False)

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            logging.info(f"Error: '{metier}' is already registered for user '{user}'.")
            embed = discord.Embed(title=f"Métier déja enregistré", color=color.YELLOW)
        else:
            logging.info(f"Error registering metier '{metier}:{level} from {user}': {e}")
    finally:
        return embed


def delete(metier: str, user: str):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")

    embed = bf.error_generic()

    try:
        cursor_obj.execute("DELETE FROM METIERS WHERE Metier = ?;", (metier,))
        changes = connection_obj.total_changes
        connection_obj.commit()
        if changes > 0:
            embed = discord.Embed(title=f"Métier supprimé", color=color.GREEN)
            embed.add_field(name=f"Metier: {metier}", inline=False)
            logging.info(f"{user} deleted '{metier}' successfully.")
        else:
            embed = discord.Embed(title=f"Métier non trouvé", color=color.YELLOW)
            logging.info(f"'{metier}' for {user} not found.")

    except sqlite3.IntegrityError as e:
        logging.info(f"Error updating metier '{metier}': {e}")

    finally:
        connection_obj.close()
        return embed


def update(metier: str, user: str, level: int):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    embed = bf.error_generic()

    try:
        cursor_obj.execute(
            """
            UPDATE METIERS 
            SET level = ?, DateUpdated = ? 
            WHERE Pseudo = ? AND Metier = ?;
            """,
            (level, current_date, user, metier)
        )
        connection_obj.commit()
        embed = discord.Embed(title=f"Métier Mis à jours", color=color.GREEN)
        embed.add_field(name=f"Metier: {metier} ", value=f"Lvl: {level}", inline=False)

        logging.info(f"{user} Updated '{metier}:{level}' successfully.")

    except sqlite3.IntegrityError as e:
        logging.info(f"Error updating metier '{metier}': {e}")

    finally:
        connection_obj.close()
        return embed


def list_artisans(metier: str, level: int):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")
    embed = bf.error_generic()

    try:
        cursor_obj.execute(
            "SELECT Pseudo, Metier, Level, DateCreated, DateUpdated FROM METIERS WHERE Metier = ? AND Level > ?;",
            (metier, level)
        )
        rows = cursor_obj.fetchall()

        if rows:
            embed = discord.Embed(title=f"Artisans de proffession {metier} avec le level mini {level}",
                                  color=color.BLUE)
            logging.info(f"Listing users register as Worker on '{metier}' and level greater than {level}:")

            for row in rows:
                logging.info(
                    f"User: {row[0]}, Metier: {row[1]}, level: {row[2]}, DateCreated: {row[3]}, DateUpdated: {row[4]}")
                embed.add_field(name=f"Pseudo: {row[0]} ", value=f"level: {row[2]}", inline=False)
        else:
            logging.info(f"No users found with Metier '{metier}' and level greater than {level}.")
            embed = discord.Embed(title=f"Aucun Artisans de proffession {metier} avec le level mini {level}",
                                  color=color.YELLOW)

    except sqlite3.Error as e:
        logging.info(f"Error fetching data: {e}")

    finally:
        connection_obj.close()
        return embed


def list_metiers_by_user(pseudo: str):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")
    embed = bf.error_generic()

    try:
        cursor_obj.execute(
            "SELECT Pseudo, Metier, Level, DateCreated, DateUpdated FROM METIERS WHERE Pseudo = ? ORDER BY Level DESC;",
            (pseudo,)
        )
        rows = cursor_obj.fetchall()
        if rows:
            embed = discord.Embed(title=f"Métier de: {pseudo}", color=color.BLUE)
            logging.info(f"Listing all metiers for user '{pseudo}':")
            for row in rows:
                embed.add_field(name=f"Metier: {row[1]} ", value=f"level: {row[2]}", inline=False)
                logging.info(f"Metier: {row[1]}, level: {row[2]}, DateCreated: {row[3]}, DateUpdated: {row[4]}")

        else:
            embed = discord.Embed(title=f"L'Artisan {pseudo} n'a enregistré aucun métier",
                                  color=color.YELLOW)
            logging.info(f"No metiers found for user '{pseudo}'.")
        return rows
    except sqlite3.Error as e:
        logging.info(f"Error fetching data: {e}")

    finally:
        connection_obj.close()
        return embed


def get_artisan_list():
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")

    try:
        cursor_obj.execute(
            "SELECT DISTINCT Pseudo FROM METIERS"
        )
        rows = cursor_obj.fetchall()
        logging.info(f"Found {len(rows)} Artisans registered")
        pseudo_list = [row[0] for row in rows]

        return pseudo_list

    except sqlite3.Error as e:
        logging.info(f"Error fetching data: {e}")

    finally:
        connection_obj.close()
