class Inventory:
    """
    Manages the player's items. Data is structured for easy manipulation
    and serialization to JSON for LLM prompt injection.
    """
    def __init__(self):
        # Dictionary to store items.
        # Key: item_id (string), Value: dictionary with item data
        self.items = {}

    def add_item(self, item_id: str, name: str, description: str, quantity: int = 1):
        if item_id in self.items:
            self.items[item_id]["quantity"] += quantity
        else:
            self.items[item_id] = {
                "name": name,
                "description": description,
                "quantity": quantity
            }

    def remove_item(self, item_id: str, quantity: int = 1):
        if item_id in self.items:
            self.items[item_id]["quantity"] -= quantity
            if self.items[item_id]["quantity"] <= 0:
                del self.items[item_id]

    def has_item(self, item_id: str) -> bool:
        """Checks if the player has a specific item."""
        return item_id in self.items and self.items[item_id]["quantity"] > 0

    def get_item_quantity(self, item_id: str) -> int:
        """Returns the quantity of a specific item."""
        if item_id in self.items:
            return self.items[item_id]["quantity"]
        return 0

    def to_dict(self) -> dict:
        """
        Returns a simplified dictionary representation of the inventory.
        Useful for generating the dynamic context for the LLM.
        Example output: {"gold": 50, "ferret_amulet": 1}
        """
        return {item_id: data["quantity"] for item_id, data in self.items.items()}
