import streamlit as st
from grocery import GroceryList, GroceryItem
import os
from db import (add_history_db, get_history_db, add_meal_db, get_meals_db, get_suggestions_db, add_item_db, get_items_db, clear_items_db, get_session, MealPlanDB)
import streamlit_authenticator as stauth
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import random
import streamlit.components.v1 as components

hashed_passwords = stauth.Hasher(['password1', 'password2']).generate()

config = {
    'credentials': {
        'usernames': {
            'user1': {
                'name': 'User One',
                'password': hashed_passwords[0]
            },
            'user2': {
                'name': 'User Two',
                'password': hashed_passwords[1]
            }
        }
    },
    'cookie': {
        'expiry_days': 1,
        'key': 'some_signature_key',
        'name': 'smart_grocery_cookie'
    },
    'preauthorized': {
        'emails': []
    }
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

st.set_page_config(page_title="Smart Grocery List Generator", page_icon="🛒", layout="wide")

st.markdown("""
<style>
    .main, .stApp {
        background: linear-gradient(135deg, #f7f9fa 0%, #e3f0ff 100%);
    }
    .grocery-card {
        background: rgba(255,255,255,0.95);
        border-radius: 18px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.07);
        padding: 1.5em 1em 1em 1em;
        margin-bottom: 1.5em;
        transition: box-shadow 0.2s;
    }
    .grocery-card:hover {
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
    }
    .grocery-img {
        border-radius: 50%;
        object-fit: cover;
        width: 60px;
        height: 60px;
        border: 2px solid #90caf9;
        margin-right: 1em;
        box-shadow: 0 2px 8px rgba(33,150,243,0.08);
    }
    .category-badge {
        display: inline-block;
        color: #00796b;
        border-radius: 8px;
        padding: 0.2em 0.7em;
        font-size: 0.9em;
        margin-left: 0.5em;
        font-weight: 600;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .stButton>button {
        border-radius: 8px !important;
        font-size: 1.1em;
        padding: 0.3em 1.2em;
        background: linear-gradient(90deg, #90caf9 0%, #64b5f6 100%);
        color: #fff;
        border: none;
        transition: background 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #64b5f6 0%, #1976d2 100%);
        color: #fff;
    }
    .stTextInput>div>input {
        border-radius: 8px;
        border: 1px solid #90caf9;
        padding: 0.5em;
    }
    .stNumberInput>div>input {
        border-radius: 8px;
        border: 1px solid #90caf9;
        padding: 0.5em;
    }
    .stFileUploader>div {
        border-radius: 8px;
        border: 1px solid #90caf9;
        background: #e3f2fd;
    }
    .stAlert {
        border-radius: 10px;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# Personalized greeting
now = datetime.now()
hour = now.hour
if hour < 12:
    greet = "Good morning ☀️"
elif hour < 18:
    greet = "Good afternoon 🌤️"
else:
    greet = "Good evening 🌙"
st.markdown(f"### {greet}, **{name or 'User'}**!")

if authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
else:
    st.success(f'Welcome {name}!')
    # Use username for all DB operations
    with st.form("add_item_form"):
        name_input = st.text_input("Item name")
        quantity = st.number_input("Quantity", min_value=1, value=1)
        category = st.text_input("Category", value="Other")
        image_file = st.file_uploader("Upload item image (optional)", type=["png", "jpg", "jpeg"], key="add_image")
        submitted = st.form_submit_button("Add Item")
        image_path = None
        if image_file is not None:
            img_dir = f"item_images/{username}"
            os.makedirs(img_dir, exist_ok=True)
            image_path = os.path.join(img_dir, image_file.name)
            with open(image_path, "wb") as f:
                f.write(image_file.read())
        if submitted and name_input:
            add_item_db(name_input, quantity, category, username, image_path)
            st.success(f"Added {name_input}")

    with st.expander("Grocery List (Database)", expanded=True):
        db_items = get_items_db(username)
        search = st.text_input("🔍 Search items", key="search_items")
        filtered_items = [item for item in db_items if search.lower() in item.name.lower()] if db_items else []
        if filtered_items:
            for idx, item in enumerate(filtered_items):
                with st.container():
                    col_img, col_info, col_edit, col_del = st.columns([1,4,1,1])
                    with col_img:
                        if getattr(item, 'image_path', None):
                            st.image(item.image_path, width=60, output_format="auto", use_column_width=False)
                    with col_info:
                        badge_color = globals().get('CATEGORY_COLORS', {}).get(item.category, "#b0bec5")
                        st.markdown(f"**{item.name}**  <span class='category-badge' style='background:{badge_color};'>{item.category}</span>  ", unsafe_allow_html=True)
                        st.write(f"Quantity: {item.quantity}")
                    with col_edit:
                        if st.button("✏️", "Edit item", key=f"edit_grocery_{item.id}_{idx}"):
                            with st.form(f"edit_form_grocery_{item.id}_{idx}"):
                                new_name = st.text_input("Name", value=item.name)
                                new_quantity = st.number_input("Quantity", min_value=1, value=item.quantity)
                                new_category = st.text_input("Category", value=item.category)
                                submitted = st.form_submit_button("Save Changes")
                                if submitted:
                                    item.name = new_name
                                    item.quantity = new_quantity
                                    item.category = new_category
                                    session = get_session()
                                    session.merge(item)
                                    session.commit()
                                    session.close()
                                    st.success("Item updated!")
                                    st.rerun()
                    with col_del:
                        if st.button("🗑️", "Delete item", key=f"delete_grocery_{item.id}_{idx}"):
                            session = get_session()
                            session.delete(item)
                            session.commit()
                            session.close()
                            st.success("Item deleted!")
                            st.rerun()
        else:
            st.info("No items in the grocery list.")

        if st.button("Clear List (Database)"):
            clear_items_db(username)
            st.success("Grocery list cleared from database.")

        if st.button("Save to History (DB)"):
            add_history_db([{ 'name': i.name, 'quantity': i.quantity, 'category': i.category } for i in db_items], username)
            st.success("Grocery list saved to database history.")
        if st.button("Show History (DB)"):
            history = get_history_db(username)
            if not history:
                st.info("No purchase history found in database.")
            else:
                for ts, items in history:
                    st.write(f"**{ts.strftime('%Y-%m-%d %H:%M:%S')}:**")
                    for item in items:
                        st.write(f"- {item['name']} (x{item['quantity']}) - {item['category']}")

    with st.expander("Shopping Mode", expanded=False):
        st.header("Shopping Mode")
        if db_items:
            checked_items = st.session_state.get("checked_items", set())
            for idx, item in enumerate(db_items):
                checked = item.id in checked_items
                col1, col2, col3 = st.columns([2,1,1])
                with col1:
                    is_checked = st.checkbox(f"{item.name} (x{item.quantity}) - {item.category}", value=checked, key=f"check_shopping_{item.id}_{idx}")
                with col2:
                    if st.button(f"Edit", "Edit item", key=f"edit_shopping_{item.id}_{idx}"):
                        with st.form(f"edit_form_shopping_{item.id}_{idx}"):
                            new_name = st.text_input("Name", value=item.name)
                            new_quantity = st.number_input("Quantity", min_value=1, value=item.quantity)
                            new_category = st.text_input("Category", value=item.category)
                            submitted = st.form_submit_button("Save Changes")
                            if submitted:
                                item.name = new_name
                                item.quantity = new_quantity
                                item.category = new_category
                                session = get_session()
                                session.merge(item)
                                session.commit()
                                session.close()
                                st.success("Item updated!")
                                st.rerun()
                with col3:
                    if st.button(f"Delete", "Delete item", key=f"delete_shopping_{item.id}_{idx}"):
                        session = get_session()
                        session.delete(item)
                        session.commit()
                        session.close()
                        st.success("Item deleted!")
                        st.rerun()
                # Update checked items in session state
                if is_checked:
                    checked_items.add(item.id)
                else:
                    checked_items.discard(item.id)
            st.session_state["checked_items"] = checked_items
        else:
            st.info("No items in the grocery list.")

        # Progress bar for shopping completion
        if db_items:
            total = len(db_items)
            checked = len(st.session_state.get("checked_items", set()))
            percent = int((checked / total) * 100) if total else 0
            st.progress(percent, text=f"Shopping completion: {percent}%")
            if percent == 100 and total > 0:
                st.balloons()

    with st.expander("Meal Planner (DB)", expanded=False):
        meal_planner_ui = globals().get('meal_planner_ui')
        if meal_planner_ui:
            meal_planner_ui()
        else:
            st.info("Meal planner not available.")

    with st.expander("Suggestions (DB)", expanded=False):
        st.header("Suggestions (DB)")
        suggestions = get_suggestions_db(username)
        if suggestions:
            for item, count in suggestions:
                st.write(f"{item.title()} (added {count} times)")
        else:
            st.info("No suggestions available yet. Add and save some lists first.")

    with st.expander("Analytics Dashboard", expanded=False):
        st.header("Analytics Dashboard")
        history = get_history_db(username)
        if history:
            all_items = []
            for ts, items in history:
                for item in items:
                    all_items.append({"name": item["name"], "quantity": item["quantity"], "date": ts})
            df = pd.DataFrame(all_items)
            if not df.empty:
                st.subheader("Most Purchased Items")
                top_items = df.groupby("name")["quantity"].sum().sort_values(ascending=False).head(5)
                st.bar_chart(top_items)
                st.subheader("Purchase Trends Over Time")
                df["date"] = pd.to_datetime(df["date"])
                trend = df.groupby(df["date"].dt.date)["quantity"].sum()
                st.line_chart(trend)
            else:
                st.info("No data for analytics yet.")
        else:
            st.info("No purchase history for analytics.")

with st.sidebar:
    st.header("👤 User Info")
    if authentication_status:
        st.write(f"**Logged in as:** {name}")
        st.write(f"**Username:** {username}")
    st.markdown("---")
    st.write("Switch Streamlit theme in settings (⚙️) for dark/light mode.")
    st.markdown("[GitHub Repo](https://github.com/) | [Help](#)")

CATEGORY_COLORS = {
    "Produce": "#a5d6a7",
    "Dairy": "#fff59d",
    "Bakery": "#ffe082",
    "Meat": "#ef9a9a",
    "Beverages": "#b3e5fc",
    "Snacks": "#ce93d8",
    "Other": "#b0bec5"
}

def tooltip_button(label, tooltip, key=None, **kwargs):
    btn = st.button(label, key=key, **kwargs)
    if btn:
        st.write(f"{tooltip}")
    return btn
