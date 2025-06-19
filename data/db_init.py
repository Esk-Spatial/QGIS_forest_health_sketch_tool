import os
import sqlite3


# Default Keypad Data
data = [
    {"category": "BMAD", "selected": False, "colour": "#FFC0CB", "items": ["Discolour", "BMAD_L", "BMAD_M", "BMAD_H", "Stags", "Other"]},
    {"category": "EUCS", "selected": False, "colour": "#00FF00", "items": ["Creiis_", "Discolour_", "Defol_", "KLD_", "MLD_", "BMAD_", "QSB_", "WinterBB_"]},
    {"category": "DEAD", "selected": False, "colour": "#FF9595", "items": ["D-tr_", "D-to_", "D-ti_", "D-tr-to-ti_"]},
    {"category": "NEEDLES", "selected": False, "colour": "#FFFFA4", "items": ["Dothi_", "Essi_", "Yelo_", "Brown_"]},
    {"category": "NUT-DEF", "selected": False, "colour": "#FFA4E1", "items": ["B-def_", "Mg-K-def_", "Nut-def_", "N-def"]},
    {"category": "WEEDS", "selected": False, "colour": "#7AB47A", "items": ["Weeds_"]},
    {"category": "POSSUM", "selected": False, "colour": "#FFA500", "items": ["Poss_"]},
    {"category": "SPH", "selected": False, "colour": "#D3D3D3", "items": ["SPH_"]},
    {"category": "INCIDENCE", "selected": False, "colour": "#FFFFe0", "items": ["1-5%", "5-15%", "15-30%", "30-45%", "45-75%", ">75%"]},
    {"category": "CLIMATE", "selected": False, "colour": "#D5D5D5", "items": ["Frost_", "Fire_", "Snow_", "Wind_", "L_", "Hail_"]},
    {"category": "SEVERITY", "selected": False, "colour": "#ADD8E6", "items": ["Low", "Moderate", "High", "Extreme"]},
    {"category": "GROUND", "selected": False, "colour": "#FFFFFF", "items": ["_Sirex", "_Drought", "_Root-H2O", "_Cyc", "_Essi", "_Herb", "_Etops", "_Yel-Tops"]},
    {"category": "Defoliating pests", "selected":False, "colour":"#FFA07A", "items":["Trace (0-10%)","Trace low","Low (10-20%)","Low Medium","Medium (20-40%)","Medium High","High (40-50%)","Severe (>50%)"]},
    {"category": "Ips and Diplodia", "selected":False, "colour":"#90EE90", "items":["Trace (<1- 2%)","Low (3 - 5%)","Medium (5 - 10%)","High (11 - 15%)","Severe (>15%)"]},
    {"category": "Sirex", "selected":False, "colour":"#87CEFA", "items":["Low (<1%)","Medium (1-3%)","Severe (>3%)"]}
]

class DbInit:
    def __init__(self, db_path):
        """Constructor.

        :param db_path: Path to the database file.
        :type db_path: str
        """
        self.db_path = db_path
        data_dir = os.path.dirname(__file__)
        os.makedirs(data_dir, exist_ok=True)


    def init_db(self):
        """Initialize the database.
        Create the Categories and Items tables and populate them with the data.
        """
        # Step 3: Create and populate a database
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS categories")
        cur.execute("DROP TABLE IF EXISTS items")

        cur.execute("""
            CREATE TABLE categories (
                cat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                selected BOOLEAN NOT NULL,
                colour TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                item TEXT NOT NULL,
                FOREIGN KEY(category_id) REFERENCES categories(id)
            )
        """)

        # Insert your data
        for entry in data:
            cur.execute("INSERT INTO categories (category, selected, colour) VALUES (?, ?, ?)",
                        (entry["category"], int(entry["selected"]), entry["colour"]))
            category_id = cur.lastrowid
            for item in entry["items"]:
                cur.execute("INSERT INTO items (category_id, item) VALUES (?, ?)",
                            (category_id, item))

        conn.commit()
        conn.close()

        print(f"Database saved at: {self.db_path}")
