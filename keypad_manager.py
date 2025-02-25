import copy

_initial_data_ = [
    {"category": "BMAD", "selected": False, "colour": "#C8B5F4", "items": ["Discolour", "BMAD_L", "BMAD_M", "BMAD_H", "Stags", "Other"]},
    {"category": "DEAD", "selected": True, "colour": "#C4BDCF", "items": ["D-tr_", "D-to_", "D-ti_", "D-tr-to_"]},
    {"category": "EUCS", "selected": False, "colour": "#EBF1BD", "items": ["Ecde_", "Defe_", "Dvev_"]},
    {"category": "NEEDLES", "selected": True, "colour": "#C3C4B4", "items": ["Dothi_", "Essi_", "Yelo_", "Brown_"]},
    {"category": "CLIMATE", "selected": False, "colour": "#B2D9FD", "items": ["Frost_", "Fire_", "Snow_", "wind_", "L_", "Hail_"]},
    {"category": "NUT-DEF", "selected": False, "colour": "#E7E4F3", "items": ["CXdedf_"]},
    {"category": "WEEDS", "selected": False, "colour": "#D3C7D8", "items": ["Weeds_"]},
    {"category": "POSSUM", "selected": False, "colour": "#DBD5D9", "items": ["Poss_"]},
    {"category": "SPH", "selected": False, "colour": "#C6C3CC", "items": ["SPH_"]},
    {"category": "INCIDENCE", "selected": False, "colour": "#D5E1BD", "items": ["_Sirex"]},
    {"category": "SEVERITY", "selected": False, "colour": "#B6CDEC", "items": ["_Drought_", "_Root-H2O", "_Cyc", "_Essi"]}
]

class Keypad:
    def __init__(self, category: str, selected: bool, colour: str, items: list):
        self.category = category
        self.selected = selected
        self.colour = colour
        self.items = items

    def __repr__(self):
        return f"Category(category='{self.category}', selected={self.selected}, colour='{self.colour}', items={self.items})"

class KeypadManager:

    def __init__(self):
        self.data = [Keypad(**data) for data in _initial_data_]
        self.data_cpy = []

    def create_data_copy(self):
        self.data_cpy = copy.deepcopy(self.data)

    def update_dataset(self):
        global _initial_data_
        _initial_data_ = [
            {"category": keypad.category, "selected": keypad.selected, "colour": keypad.colour, "items": keypad.items}
            for keypad in self.data_cpy
        ]
        self.data = [Keypad(**data) for data in _initial_data_]

    def get_selected_categories(self):
        return filter(lambda category: category.selected == True, self.data)

    def add_category(self, data):
        if any(cat.category != data.category for cat in self.data_cpy):
            self.data_cpy.append(data)

    def add_item(self, category_name, data):
        category = next((cat for cat in self.data_cpy if cat.category == category_name), None)
        if category:
            category.items.append(data)

    def move_category(self, category_name, direction):
        """Moves a category up or down."""
        index = next((i for i, cat in enumerate(self.data_cpy) if cat.category == category_name), None)
        if index is None:
            print(f"Category '{category_name}' not found.")
            return
        if direction == "up" and index > 0:
            self.data_cpy[index], self.data_cpy[index - 1] = self.data_cpy[index - 1], self.data_cpy[index]
        elif direction == "down" and index < len(self.data_cpy) - 1:
            self.data_cpy[index], self.data_cpy[index + 1] = self.data_cpy[index + 1], self.data_cpy[index]

    def move_item(self, category_name, item, direction):
        """Moves an item up or down within a category."""
        category = next((cat for cat in self.data_cpy if cat.category == category_name), None)
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
        self.data_cpy = [cat for cat in self.data_cpy if cat.category != category_name]

    def remove_item(self, category_name, item):
        """Removes an item from a category."""
        category = next((cat for cat in self.data_cpy if cat.category == category_name), None)
        if category:
            category.items = [i for i in category.items if i != item]

    def set_category_selection(self, category_name, state):
        category = next((cat for cat in self.data_cpy if cat.category == category_name), None)
        if category:
            selection = state == 2
            category.selected = selection

    def set_category_colour(self, category_name, colour):
        category = next((cat for cat in self.data_cpy if cat.category == category_name), None)
        if category:
            category.colour = colour