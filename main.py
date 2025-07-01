# main.py

import json
import os
from collections import Counter
from typing import List
import datetime
import csv

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

    def __str__(self):
        return f"{self.name} (x{self.quantity}) - {self.category}"

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
        if not self.items:
            print("No items in the grocery list.")
        for item in self.items:
            print(item)

    def clear(self):
        self.items = []

    def to_dict(self):
        return [item.to_dict() for item in self.items]

    def from_dict(self, data):
        self.items = [GroceryItem.from_dict(item) for item in data]

class HistoryManager:
    def __init__(self, filename="history.json"):
        self.filename = filename
        self.history = self.load_history()

    def load_history(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        return []

    def save_history(self, grocery_list: GroceryList):
        self.history.append(grocery_list.to_dict())
        with open(self.filename, "w") as f:
            json.dump(self.history, f, indent=2)

    def show_history(self):
        if not self.history:
            print("No purchase history found.")
            return
        for i, purchase in enumerate(self.history, 1):
            print(f"Purchase {i}:")
            for item in purchase:
                print(f"  {item['name']} (x{item['quantity']}) - {item['category']}")

class SuggestionEngine:
    def __init__(self, history_manager: HistoryManager):
        self.history_manager = history_manager

    def suggest_items(self, top_n=5):
        all_items = []
        for purchase in self.history_manager.history:
            for item in purchase:
                all_items.append(item['name'].lower())
        if not all_items:
            print("No suggestions available yet. Add and save some lists first.")
            return
        counter = Counter(all_items)
        print(f"Top {top_n} suggested items:")
        for item, count in counter.most_common(top_n):
            print(f"  {item.title()} (added {count} times)")

class MealPlanner:
    def __init__(self, filename="meals.json"):
        self.filename = filename
        self.meals = self.load_meals()

    def load_meals(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        return {}

    def save_meals(self):
        with open(self.filename, "w") as f:
            json.dump(self.meals, f, indent=2)

    def add_meal(self, date: str, items: List[str]):
        self.meals[date] = items
        self.save_meals()
        print(f"Meal for {date} saved.")

    def show_meals(self):
        if not self.meals:
            print("No meals planned.")
            return
        for date, items in self.meals.items():
            print(f"{date}: {', '.join(items)})")

class Optimizer:
    @staticmethod
    def optimize_list(grocery_list: GroceryList):
        # Example: group by category and sort alphabetically
        grouped = {}
        for item in grocery_list.items:
            grouped.setdefault(item.category, []).append(item)
        for category in sorted(grouped):
            print(f"\n{category}:")
            for item in sorted(grouped[category], key=lambda x: x.name):
                print(f"  {item}")

class Exporter:
    @staticmethod
    def export_to_csv(grocery_list: GroceryList, filename: str = "grocery_list.csv"):
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Name", "Quantity", "Category"])
            for item in grocery_list.items:
                writer.writerow([item.name, item.quantity, item.category])
        print(f"Grocery list exported to {filename}.")

class Importer:
    @staticmethod
    def import_from_csv(grocery_list: GroceryList, filename: str = "grocery_list.csv"):
        if not os.path.exists(filename):
            print(f"File {filename} does not exist.")
            return
        with open(filename, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                grocery_list.add_item(GroceryItem(row["Name"], int(row["Quantity"]), row["Category"]))
        print(f"Grocery list imported from {filename}.")

class Reminder:
    @staticmethod
    def remind_if_empty(grocery_list: GroceryList):
        if not grocery_list.items:
            print("Reminder: Your grocery list is empty! Add items before shopping.")

# CLI
def main():
    print("Hello, World! This is your Smart Grocery List Generator.")
    grocery_list = GroceryList()
    history_manager = HistoryManager()
    suggestion_engine = SuggestionEngine(history_manager)
    meal_planner = MealPlanner()
    while True:
        print("\nOptions: add, remove, edit, list, save, history, suggest, clear, mealplan, meals, optimize, export, import, remind, quit")
        cmd = input("Enter command: ").strip().lower()
        if cmd == "add":
            name = input("Item name: ")
            try:
                quantity = int(input("Quantity: "))
            except ValueError:
                print("Invalid quantity. Defaulting to 1.")
                quantity = 1
            category = input("Category: ")
            grocery_list.add_item(GroceryItem(name, quantity, category))
            print(f"Added {name}.")
        elif cmd == "remove":
            name = input("Item name to remove: ")
            grocery_list.remove_item(name)
            print(f"Removed {name}.")
        elif cmd == "edit":
            name = input("Item name to edit: ")
            quantity = input("New quantity (leave blank to skip): ")
            category = input("New category (leave blank to skip): ")
            grocery_list.edit_item(
                name,
                int(quantity) if quantity else None,
                category if category else None
            )
            print(f"Edited {name}.")
        elif cmd == "list":
            grocery_list.list_items()
        elif cmd == "save":
            history_manager.save_history(grocery_list)
            print("Grocery list saved to history.")
        elif cmd == "history":
            history_manager.show_history()
        elif cmd == "suggest":
            suggestion_engine.suggest_items()
        elif cmd == "clear":
            grocery_list.clear()
            print("Grocery list cleared.")
        elif cmd == "mealplan":
            date = input("Enter date (YYYY-MM-DD): ")
            items = input("Enter meal items (comma separated): ").split(",")
            meal_planner.add_meal(date, [item.strip().title() for item in items])
        elif cmd == "meals":
            meal_planner.show_meals()
        elif cmd == "optimize":
            Optimizer.optimize_list(grocery_list)
        elif cmd == "export":
            Exporter.export_to_csv(grocery_list)
        elif cmd == "import":
            Importer.import_from_csv(grocery_list)
        elif cmd == "remind":
            Reminder.remind_if_empty(grocery_list)
        elif cmd == "quit":
            print("Goodbye!")
            break
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
