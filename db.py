from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import os
from collections import Counter

Base = declarative_base()

class GroceryItemDB(Base):
    __tablename__ = 'grocery_items'
    id = Column(Integer, primary_key=True)
    username = Column(String)  # New: associate item with user
    name = Column(String)
    quantity = Column(Integer)
    category = Column(String)
    image_path = Column(String, nullable=True)  # New: path to uploaded image (optional)

class GroceryHistoryDB(Base):
    __tablename__ = 'grocery_history'
    id = Column(Integer, primary_key=True)
    username = Column(String)  # New: associate history with user
    timestamp = Column(DateTime, default=func.now())
    items = Column(String)  # JSON string of items

class MealPlanDB(Base):
    __tablename__ = 'meal_plans'
    id = Column(Integer, primary_key=True)
    username = Column(String)  # New: associate meal with user
    date = Column(String)
    items = Column(String)  # JSON string of meal items

def get_engine():
    return create_engine('sqlite:///grocery.db', echo=False)

def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)

# Ensure tables are created at import time
create_tables()

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def add_item_db(name, quantity, category, username, image_path=None):
    session = get_session()
    item = GroceryItemDB(name=name, quantity=quantity, category=category, username=username, image_path=image_path)
    session.add(item)
    session.commit()
    session.close()

def get_items_db(username):
    session = get_session()
    items = session.query(GroceryItemDB).filter_by(username=username).all()
    session.close()
    return items

def clear_items_db(username):
    session = get_session()
    session.query(GroceryItemDB).filter_by(username=username).delete()
    session.commit()
    session.close()

def add_history_db(items, username):
    session = get_session()
    history = GroceryHistoryDB(items=json.dumps(items), username=username)
    session.add(history)
    session.commit()
    session.close()

def get_history_db(username):
    session = get_session()
    history = session.query(GroceryHistoryDB).filter_by(username=username).order_by(GroceryHistoryDB.timestamp.desc()).all()
    session.close()
    return [(h.timestamp, json.loads(h.items)) for h in history]

def add_meal_db(date, items, username):
    session = get_session()
    meal = MealPlanDB(date=date, items=json.dumps(items), username=username)
    session.add(meal)
    session.commit()
    session.close()

def get_meals_db(username):
    session = get_session()
    meals = session.query(MealPlanDB).filter_by(username=username).all()
    session.close()
    return [(m.date, json.loads(m.items)) for m in meals]

def get_suggestions_db(username, top_n=5):
    history = get_history_db(username)
    all_items = []
    for _, purchase in history:
        for item in purchase:
            all_items.append(item['name'].lower())
    counter = Counter(all_items)
    return counter.most_common(top_n)
