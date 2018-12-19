from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from config import DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT

# Connect to server
uri = f'mysql+pymysql://{ DATABASE_USER }:{ DATABASE_PASSWORD }@{ DATABASE_HOST}:{ DATABASE_PORT }/toc_final_project'
engine = create_engine(uri, max_overflow = 5)

# Auto generate model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Get table model, including relationship
Drink = Base.classes.drink
Sweetness = Base.classes.sweetness
Ice = Base.classes.ice
Topping = Base.classes.topping

# Create session for database operating
session = Session(engine)

def get_popular_drink():
    result = session.query(Drink.name).order_by(Drink.sale_count.desc(), Drink.drink_id.asc()).limit(3)
    return [x[0] for x in list(result)]

def get_drink_info(drink_name):
    result = session.query(Drink.drink_id, Drink.price).filter(Drink.name == drink_name).first()
    return result

def get_sweetness(drink_id):
    try:
        result = session.query(Sweetness.name).join(Drink.sweetness_collection).filter(Drink.drink_id == drink_id).all()
    except AttributeError:
        result = session.query(Sweetness.name).join(Sweetness.drink_collection).filter(Drink.drink_id == drink_id).all()
    return [x[0] for x in list(result)]

def get_ice(drink_id):
    try:
        result = session.query(Ice.name).join(Drink.ice_collection).filter(Drink.drink_id == drink_id).all()
    except AttributeError:
        result = session.query(Ice.name).join(Ice.drink_collection).filter(Drink.drink_id == drink_id).all()
    return [x[0] for x in list(result)]

def get_topping():
    result = session.query(Topping.name, Topping.price).all()
    return result

def update_sale_count(order_list):
    for order in order_list:
        session.query(Drink).filter(Drink.drink_id == order['id']).update({"sale_count": Drink.sale_count + 1}, synchronize_session="evaluate")
    session.commit()