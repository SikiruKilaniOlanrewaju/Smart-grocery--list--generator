from flask import Flask, request, jsonify, render_template_string
from grocery import GroceryList, GroceryItem

grocery_list = GroceryList()

app = Flask(__name__)

@app.route('/')
def index():
    items = grocery_list.list_items()
    return render_template_string('''
        <h1>Smart Grocery List Generator</h1>
        <form method="post" action="/add">
            <input name="name" placeholder="Item name" required>
            <input name="quantity" type="number" min="1" value="1" required>
            <input name="category" placeholder="Category" required>
            <button type="submit">Add Item</button>
        </form>
        <h2>Grocery List</h2>
        <ul>
        {% for item in items %}
            <li>{{item['name']}} (x{{item['quantity']}}) - {{item['category']}}</li>
        {% endfor %}
        </ul>
    ''', items=items)

@app.route('/add', methods=['POST'])
def add_item():
    name = request.form['name']
    quantity = int(request.form['quantity'])
    category = request.form['category']
    grocery_list.add_item(GroceryItem(name, quantity, category))
    return ('', 204), 204, {'HX-Redirect': '/'}

@app.route('/api/items', methods=['GET'])
def api_list_items():
    return jsonify(grocery_list.list_items())

if __name__ == '__main__':
    app.run(debug=True)
