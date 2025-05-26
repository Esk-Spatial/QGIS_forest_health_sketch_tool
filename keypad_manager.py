import copy
from PyQt5.QtCore import Qt

from data.db_handler import DbHandler

class Keypad:
    def __init__(self, cat_id: int, category: str, selected: bool, colour: str, items: list):
        """Initializes a new Keypad Category object.

        :param cat_id: The category ID.
        :type cat_id: int

        :param category: The category name.
        :type category: str

        :param selected: Whether the category is selected.
        :type selected: bool

        :param colour: The category colour as a Hex.
        :type colour: str

        :param items: A list of items in the category.
        :type items: list[dict]
        """
        self.cat_id = cat_id
        self.category = category
        self.selected = selected
        self.colour = colour
        self.items = [KeypadItem(**data) for data in items]

    def __repr__(self):
        """Returns a string representation of the Keypad Category object.

        :return: A string representation of the Keypad Category object.
        """
        return f"Category(cat_id={self.cat_id}, category='{self.category}', selected={self.selected}, colour='{self.colour}', items={self.items})"

class KeypadItem:
    def __init__(self, item_id, item):
        """Initializes a new Keypad Item object.

        :param item_id: The item ID.
        :type item_id: int

        :param item: The item name.
        :type item: str
        """
        self.item_id = item_id
        self.item = item

    def __repr__(self):
        """Returns a string representation of the Keypad Item object.

        :return: A string representation of the Keypad Item object.
        """
        return f"Item(item_id={self.item_id}, item='{self.item}')"

class KeypadManager:
    def __init__(self):
        """Initializes a new KeypadManager object.
        Create a DbHandler object to handle database operations.
        """
        self.data = []
        self.db_handler = DbHandler()


    def load_data(self):
        """Loads the keypad data from the database."""
        self.data = [Keypad(**data) for data in self.db_handler.load_keypad_data()]


    def update_dataset(self):
        """Updates the keypad data in the database.
        Once the apply setting is called, the data is updated in the database.
        """
        self.db_handler.reset_and_update(self.data)


    def get_selected_categories(self):
        """Returns a list of selected categories.

        :return: A list of selected categories.
        """
        return filter(lambda category: category.selected == True, self.data)


    def add_category(self, data):
        """Adds a new category to the keypad data.

        :param data: The category data to add.
        """
        if any(cat.category != data.category for cat in self.data):
            self.data.append(data)


    def add_item(self, category_name, data):
        """Adds a new item to a category.
        Get the category object by name and append the item to the category's items list.

        :param category_name: The name of the category to add the item to.
        :type category_name: str

        :param data: The item data to add.
        :type data: dict
        """
        category = self.get_category_by_name(category_name)
        if category:
            category.items.append(data)


    def move_category(self, category_name, direction):
        """Moves a category up or down.

        :param category_name: The name of the category to move.
        :type category_name: str

        :param direction: The direction to move the category. Possible values are "up" and "down.
        :type direction: str
        """
        index = next((i for i, cat in enumerate(self.data) if cat.category == category_name), None)
        if index is None:
            print(f"Category '{category_name}' not found.")
            return
        if direction == "up" and index > 0:
            self.data[index], self.data[index - 1] = self.data[index - 1], self.data[index]
        elif direction == "down" and index < len(self.data) - 1:
            self.data[index], self.data[index + 1] = self.data[index + 1], self.data[index]


    def move_item(self, category_name, item, direction):
        """Moves an item up or down within a category.

        :param category_name: The name of the category.
        :type category_name: str

        :param item: The name of the category to move.
        :type item: str

        :param direction: The direction to move the item. Possible values are "up" and "down.
        :type direction: str
        """
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
        """Removes a category.

        :param category_name: The name of the category to remove.
        :type category_name: str
        """
        self.data = [cat for cat in self.data if cat.category != category_name]


    def remove_item(self, category_name, item):
        """Removes an item from a category.
        Find the category by Name and if found, remove the item from the category's  item list.

        :param category_name: The name of the category.
        :type category_name: str

        :param item: The name of the item to remove.
        :type item: str
        """
        category = self.get_category_by_name(category_name)
        if category:
            category.items = [i for i in category.items if i.item != item]


    def set_category_selection(self, category_name, state):
        """Set the selection state of a category.
        Find the category by Name and if found, update the selection state.

        :param category_name: The name of the category.
        :type category_name: str

        :param state: The selection state.
        :type state: int
        """
        category = self.get_category_by_name(category_name)
        if category:
            selection = state == Qt.Checked
            category.selected = selection


    def set_category_colour(self, category_name, colour):
        """Set the colour of a category.
        Find the category by Name and if found, update the colour.

        :param category_name: The name of the category.
        :type category_name: str

        :param colour: The colour as a Hex.
        :type colour: str
        """
        category = self.get_category_by_name(category_name)
        if category:
            category.colour = colour

    def update_item(self, category_name, old_name, new_name):
        """update an item name from a category.
        Find the category by Name and if found, update the item name.

        :param category_name: The name of the category.
        :type category_name: str

        :param old_name: The old name of the item.
        :type old_name: str

        :param new_name: The new name of the item.
        :type new_name: KeypadItem
        """
        category = self.get_category_by_name(category_name)
        if category:
            category.items = [new_name.item if i == old_name else i for i in category.items]

    def get_category_by_name(self, category_name):
        """Get a category by name.

        :param category_name: The name of the category.
        :type category_name: str

        :return: The category object if found, None otherwise.
        """
        return next((cat for cat in self.data if cat.category == category_name), None)

    def clear_selection(self):
        for cat in self.data:
            self.set_category_selection(cat.category, 0)

    def get_checked_category_items(self):
        """Get the checked category items.

        :return: List of checked category items.
        """
        return self.db_handler.get_checked_category_items()
