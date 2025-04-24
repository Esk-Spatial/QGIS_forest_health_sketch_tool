import copy
from PyQt5.QtCore import Qt

from data.db_handler import DbHandler
from qgis.core import QgsApplication

class Keypad:
    def __init__(self, cat_id: int, category: str, selected: bool, colour: str, items: list):
        self.cat_id = cat_id
        self.category = category
        self.selected = selected
        self.colour = colour
        self.items = [KeypadItem(**data) for data in items]

    def __repr__(self):
        return f"Category(cat_id={self.cat_id}, category='{self.category}', selected={self.selected}, colour='{self.colour}', items={self.items})"

class KeypadItem:
    def __init__(self, item_id, item):
        self.item_id = item_id
        self.item = item

    def __repr__(self):
        return f"Item(item_id={self.item_id}, item='{self.item}')"

class KeypadManager:

    def __init__(self):
        self.data = []
        self.db_handler = DbHandler()

    def load_data(self):
        self.data = [Keypad(**data) for data in self.db_handler.load_keypad_data()]

    def update_dataset(self):
        self.db_handler.reset_and_update(self.data)

    def get_selected_categories(self):
        return filter(lambda category: category.selected == True, self.data)

    def add_category(self, data):
        if any(cat.category != data.category for cat in self.data):
            self.data.append(data)

    def add_item(self, category_name, data):
        category = self.get_category_by_name(category_name)
        if category:
            category.items.append(data)

    def move_category(self, category_name, direction):
        """Moves a category up or down."""
        index = next((i for i, cat in enumerate(self.data) if cat.category == category_name), None)
        if index is None:
            print(f"Category '{category_name}' not found.")
            return
        if direction == "up" and index > 0:
            self.data[index], self.data[index - 1] = self.data[index - 1], self.data[index]
        elif direction == "down" and index < len(self.data) - 1:
            self.data[index], self.data[index + 1] = self.data[index + 1], self.data[index]

    def move_item(self, category_name, item, direction):
        """Moves an item up or down within a category."""
        category = self.get_category_by_name(category_name)
        if category is None:
            print(f"Category '{category_name}' not found.")
            return
        items = category.items
        index = items.index(item) if item in items else None
        if index is None:
            print(f"Item '{item}' not found in '{category_name}'.")
            return
        if direction == "up" and index > 0:
            items[index], items[index - 1] = items[index - 1], items[index]
        elif direction == "down" and index < len(items) - 1:
            items[index], items[index + 1] = items[index + 1], items[index]

    def remove_category(self, category_name):
        """Removes a category."""
        self.data = [cat for cat in self.data if cat.category != category_name]

    def remove_item(self, category_name, item):
        """Removes an item from a category."""
        category = self.get_category_by_name(category_name)
        if category:
            category.items = [i for i in category.items if i.item != item]

    def set_category_selection(self, category_name, state):
        category = self.get_category_by_name(category_name)
        if category:
            selection = state == Qt.Checked
            category.selected = selection

    def set_category_colour(self, category_name, colour):
        category = self.get_category_by_name(category_name)
        if category:
            category.colour = colour

    def update_item(self, category_name, old_name, new_name):
        """update an item name from a category."""
        category = self.get_category_by_name(category_name)
        if category:
            category.items = [new_name.item if i == old_name else i for i in category.items]

    def get_category_by_name(self, category_name):
        return next((cat for cat in self.data if cat.category == category_name), None)

    def clear_selection(self):
        for cat in self.data:
            self.set_category_selection(cat.category, 0)