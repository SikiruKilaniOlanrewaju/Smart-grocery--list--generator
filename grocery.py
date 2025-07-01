# grocery.py
import json
import os
from collections import Counter
from typing import List

class GroceryItem:
    def __init__(self, name: str, quantity: int = 1, category: str = "Other"):
        self.name = name.strip().title()
        self.quantity = quantity
        self.category = category.strip().title()

    def to_dict(self):
        return {"name": self.name, "quantity": self.quantity, "category": self.category}

    @staticmethod
    def from_dict(data):
        return GroceryItem(data["name"], data["quantity"], data["category"])

class GroceryList:
    def __init__(self):
        self.items: List[GroceryItem] = []

    def add_item(self, item: GroceryItem):
        for existing in self.items:
            if existing.name == item.name:
                existing.quantity += item.quantity
                return
        self.items.append(item)

    def remove_item(self, name: str):
        self.items = [item for item in self.items if item.name.lower() != name.lower()]

    def edit_item(self, name: str, quantity: int = None, category: str = None):
        for item in self.items:
            if item.name.lower() == name.lower():
                if quantity is not None:
                    item.quantity = quantity
                if category is not None:
                    item.category = category.strip().title()

    def list_items(self):
        return [item.to_dict() for item in self.items]

    def clear(self):
        self.items = []

    def to_dict(self):
        return [item.to_dict() for item in self.items]

    def from_dict(self, data):
        self.items = [GroceryItem.from_dict(item) for item in data]
