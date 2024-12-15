from datetime import datetime
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# Helper: Register Zone
def register(metier: str, user: str, lvl: int):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        cursor_obj.execute(
            "INSERT INTO METIERS (Pseudo, Metier, Lvl, DateCreated, DateUpdated) VALUES (?, ?, ?, ?, ?);",
            (user, metier, lvl, current_date, current_date)
        )
        connection_obj.commit()
        logging.info(f"{user} registed '{metier}:{lvl}' successfully.")
    except sqlite3.IntegrityError as e:
        logging.info(f"Error registering metier '{metier}': {e}")
    finally:
        connection_obj.close()


# Helper: Delete Zone
def delete(metier: str, user: str):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")

    try:
        cursor_obj.execute("DELETE FROM ZONES WHERE ZONE = ?;", (metier,))
        changes = connection_obj.total_changes
        connection_obj.commit()
        if changes > 0:
            logging.info(f"{user} deleted '{metier}' successfully.")
            return True
        else:
            logging.info(f"'{metier}' for {user} not found.")
            return False
    finally:
        connection_obj.close()

def update(metier: str, user: str, lvl: int):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # Update statement for updating Lvl and DateUpdated
        cursor_obj.execute(
            """
            UPDATE METIERS 
            SET Lvl = ?, DateUpdated = ? 
            WHERE Pseudo = ? AND Metier = ?;
            """,
            (lvl, current_date, user, metier)
        )
        connection_obj.commit()
        logging.info(f"{user} Updated '{metier}:{lvl}' successfully.")
    except sqlite3.IntegrityError as e:
        logging.info(f"Error updating metier '{metier}': {e}")
    finally:
        connection_obj.close()


# Function to list all rows where Metier matches and Lvl is greater than lvl
def list_artisans(metier: str, lvl: int):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")

    try:
        cursor_obj.execute(
            "SELECT Pseudo, Metier, Lvl, DateCreated, DateUpdated FROM METIERS WHERE Metier = ? AND Lvl > ?;",
            (metier, lvl)
        )
        rows = cursor_obj.fetchall()

        if rows:
            logging.info(f"Listing users with Metier '{metier}' and Lvl greater than {lvl}:")
            for row in rows:
                logging.info(
                    f"User: {row[0]}, Metier: {row[1]}, Lvl: {row[2]}, DateCreated: {row[3]}, DateUpdated: {row[4]}")
        else:
            logging.info(f"No users found with Metier '{metier}' and Lvl greater than {lvl}.")
        return rows
    except sqlite3.Error as e:
        logging.info(f"Error fetching data: {e}")
    finally:
        connection_obj.close()


# Function to list all metiers for a given Pseudo (user)
def list_metiers_by_user(pseudo: str):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")

    try:
        cursor_obj.execute(
            "SELECT Pseudo, Metier, Lvl, DateCreated, DateUpdated FROM METIERS WHERE Pseudo = ?;",
            (pseudo,)
        )
        rows = cursor_obj.fetchall()

        if rows:
            logging.info(f"Listing all metiers for user '{pseudo}':")
            for row in rows:
                logging.info(f"Metier: {row[1]}, Lvl: {row[2]}, DateCreated: {row[3]}, DateUpdated: {row[4]}")
        else:
            logging.info(f"No metiers found for user '{pseudo}'.")
        return rows
    except sqlite3.Error as e:
        logging.info(f"Error fetching data: {e}")
    finally:
        connection_obj.close()
