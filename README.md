# Smart Grocery List Generator

This project is a Python application designed to help users generate smart, efficient grocery lists based on their preferences, past purchases, and meal planning needs.

## Features
- Add, edit, and remove grocery items
- Generate optimized shopping lists
- Track purchase history
- Suggest items based on previous lists
- Simple command-line interface (CLI)

## Getting Started

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Run the application:**
   ```sh
   python main.py
   ```

## Project Structure
- `main.py` — Entry point for the application
- `requirements.txt` — List of Python dependencies
- `.github/copilot-instructions.md` — Copilot custom instructions
- `.vscode/tasks.json` — VS Code task configuration

## Implementation Plan

The following modules and features will be implemented:

1. **GroceryItem class**: Represents an item with name, quantity, and category.
2. **GroceryList class**: Manages a list of GroceryItem objects (add, edit, remove, list).
3. **HistoryManager**: Tracks and loads previous purchases from a file (e.g., JSON or CSV).
4. **SuggestionEngine**: Suggests items based on history and patterns.
5. **CLI Interface**: Simple command-line interface for user interaction.

## Next Steps
- Implement `GroceryItem` and `GroceryList` classes in `main.py` or a new module.
- Add basic CLI commands for adding, editing, removing, and listing items.
- Add persistence (save/load lists and history).
- Implement suggestion logic.

## Contributing
Feel free to fork this project and submit pull requests.

## License
This project is open source and available under the MIT License.
