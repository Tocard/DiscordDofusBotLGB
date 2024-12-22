import sqlite3


def run_init_sql():
    connection_obj = sqlite3.connect('lbg.db')
    cursor_obj = connection_obj.cursor()

    cursor_obj.execute("PRAGMA foreign_keys = ON;")

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

    for table in tables:
        cursor_obj.execute(table)

    connection_obj.commit()
    connection_obj.close()