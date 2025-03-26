import copy

_initial_data_ = [
  {"category": "BMAD", "selected": False, "colour": "#FFC0CB", "items": ["Discolour", "BMAD_L", "BMAD_M", "BMAD_H", "Stags", "Other"]},
  {"category": "CLIMATE", "selected": False, "colour": "#D5D5D5", "items": ["Frost_", "Fire_", "Snow_", "Wind_", "L_", "Hail_"]},
  {"category": "DEAD", "selected": False, "colour": "#FF9595", "items": ["D-tr_", "D-to_", "D-ti_", "D-tr-to-ti_"]},
  {"category": "EUCS", "selected": False, "colour": "#00FF00", "items": ["Creiis_", "Discolour_", "Defol_", "KLD_", "MLD_", "BMAD_", "QSB_", "WinterBB_"]},
  {"category": "GROUND", "selected": False, "colour": "#FFFFFF", "items": ["_Sirex", "_Drought", "_Root-H2O", "_Cyc", "_Essi", "_Herb", "_Etops", "_Yel-Tops"]},
  {"category": "INCIDENCE", "selected": False, "colour": "#FFFFe0", "items": ["1-5%", "5-15%", "15-30%", "30-45%", "45-75%", ">75%"]},
  {"category": "NEEDLES", "selected": False, "colour": "#FFFFA4", "items": ["Dothi_", "Essi_", "Yelo_", "Brown_"]},
  {"category": "NUT-DEF", "selected": False, "colour": "#FFC0CB", "items": ["B-def_", "Mg-K-def_", "Nut-def_", "N-def"]},
  {"category": "POSSUM", "selected": False, "colour": "#FFA500", "items": ["Poss_"]},
  {"category": "SEVERITY", "selected": False, "colour": "#ADD8E6", "items": ["Low", "Moderate", "High", "Extreme"]},
  {"category": "SPH", "selected": False, "colour": "#D3D3D3", "items": ["SPH_"]},
  {"category": "WEEDS", "selected": False, "colour": "#7AB47A", "items": ["Weeds_"]}
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
        category = self.get_category_by_name(category_name)
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
        self.data_cpy = [cat for cat in self.data_cpy if cat.category != category_name]

    def remove_item(self, category_name, item):
        """Removes an item from a category."""
        category = self.get_category_by_name(category_name)
        if category:
            category.items = [i for i in category.items if i != item]

    def set_category_selection(self, category_name, state):
        category = self.get_category_by_name(category_name)
        if category:
            selection = state == 2
            category.selected = selection

    def set_category_colour(self, category_name, colour):
        category = self.get_category_by_name(category_name)
        if category:
            category.colour = colour

    def update_item(self, category_name, old_name, new_name):
        """update an item name from a category."""
        category = self.get_category_by_name(category_name)
        if category:
            category.items = [new_name if i == old_name else i for i in category.items]

    def get_category_by_name(self, category_name):
        return next((cat for cat in self.data_cpy if cat.category == category_name), None)