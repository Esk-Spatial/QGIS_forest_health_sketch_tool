import os
import sqlite3


class DbHandler:
    def __init__(self):
        """Constructor.
        SQLite database handler.
        Used to retrieve and update the keypad data.
        """
        self.plugin_dir = os.path.dirname(__file__)
        self.db_path = os.path.join(self.plugin_dir, 'keypad_data.sqlite')

    def load_keypad_data(self):
        """Load the keypad data from the database.

        :return: Keypad data
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM categories")
            keypad_rows = cur.fetchall()

            keypad_data = []
            for cat_id, category, selected, colour in keypad_rows:
                cur.execute("SELECT item_id, item FROM items WHERE category_id = ?", (cat_id,))
                items = [{"item_id": row[0] , "item": row[1]} for row in cur.fetchall()]

                keypad_data.append({
                    "cat_id": cat_id,
                    "category": category,
                    "selected": bool(selected),
                    "colour": colour,
                    "items": items
                })

            return keypad_data


    def reset_and_update(self, data):
        """Reset and update the keypad data in the database.

        :param data: Keypad data
        :type data: list of dicts
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            # clearing data
            cur.execute("DELETE FROM items")
            cur.execute("DELETE FROM categories")

            # resetting auto-increment id
            cur.execute("DELETE FROM sqlite_sequence WHERE name='categories'")
            cur.execute("DELETE FROM sqlite_sequence WHERE name='items'")

            for category in data:
                cur.execute("""
                        INSERT INTO categories (category, selected, colour)
                        VALUES (?, ?, ?)
                    """, (category.category, int(category.selected), category.colour))
                category_id = cur.lastrowid

                for item in category.items:
                    cur.execute("""
                            INSERT INTO items (category_id, item)
                            VALUES (?, ?)
                        """, (category_id, item.item))

            conn.commit()


    def get_checked_category_items(self):
        """Get the checked category items from the database.

        :return: Category items
        :type: list of dicts
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            query = ("SELECT i.item, c.selected, c.colour FROM items as i "
                     "INNER JOIN categories as c on i.category_id = c.cat_id "
                     "WHERE c.selected = 1")
            cur.execute(query)
            item_rows = cur.fetchall()

            item_data = []
            for item, selected, colour in item_rows:
                item_data.append({
                    "item": item,
                    "selected": selected,
                    "colour": colour
                })

            return item_data