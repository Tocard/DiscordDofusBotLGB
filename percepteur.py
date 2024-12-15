from datetime import datetime
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# Helper: Register Zone
def register_zone(zone_name: str, user: str, is_locked: bool = False):
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
        logging.info(f"Zone '{zone_name}' registered successfully.")
    except sqlite3.IntegrityError as e:
        logging.info(f"Error registering zone '{zone_name}': {e}")
    finally:
        connection_obj.close()


# Helper: Delete Zone
def delete_zone(zone_name: str):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    cursor_obj.execute("PRAGMA foreign_keys = ON;")

    try:
        cursor_obj.execute("DELETE FROM ZONES WHERE ZONE = ?;", (zone_name,))
        changes = connection_obj.total_changes
        connection_obj.commit()
        if changes > 0:
            logging.info(f"Zone '{zone_name}' deleted successfully.")
            return True
        else:
            logging.info(f"Zone '{zone_name}' not found.")
            return False
    finally:
        connection_obj.close()


# Helper: Reserve Zone
def reserve_zone(zone_name: str, user: str):
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
        logging.info(f"Zone '{zone_name}' reserved successfully.")
    except sqlite3.IntegrityError as e:
        logging.info(f"Error reserving zone '{zone_name}': {e}")
    finally:
        connection_obj.close()


# Helper: Free Zone
def free_zone(zone_name: str):
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
        logging.info(f"Zone '{zone_name}' freed successfully.")
    except sqlite3.IntegrityError as e:
        logging.info(f"Error freeing zone '{zone_name}': {e}")
    finally:
        connection_obj.close()


def list_zone(zone: str):
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    try:
        cursor_obj.execute("SELECT * FROM ZONES WHERE ZONE = ?;", (zone,))
        rows = cursor_obj.fetchall()
        return rows

    finally:
        connection_obj.close()

def list_all_zone():
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()
    try:
        cursor_obj.execute("SELECT * FROM ZONES;")
        zones = cursor_obj.fetchall()
        return zones
    finally:
        connection_obj.close()