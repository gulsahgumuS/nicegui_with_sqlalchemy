from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from nicegui import ui
from alembic import context
from alembic.config import Config
from alembic import command

DATABASE_URL = 'sqlite:///data.db'
engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)  
    name = Column(String, nullable=False)  
    password = Column(String, nullable=False)  

target_metadata = Base.metadata  

Session = sessionmaker(bind=engine)
session = Session()

def resequence_ids():
    items = session.query(Item).order_by(Item.id).all()
    for index, item in enumerate(items, start=1):
        item.id = index
    session.commit()
    refresh_items_list()

def add_item(name, password):
    if name and password:
        new_item = Item(name=name, password=password)
        session.add(new_item)
        session.commit()
        ui.notify('Item added successfully!', color='green')
        refresh_items_list()
    else:
        ui.notify('Please fill out all fields.', color='red')

def get_items():
    return session.query(Item).order_by(Item.id).all()

def refresh_items_list():
    items = get_items()
    rows = [{'ID': item.id, 'Name': item.name, 'Password': item.password} for item in items]
    global_table.rows = rows
    print("Table updated with rows:", rows)

def delete_item(item_id):
    try:
        item = session.query(Item).filter_by(id=int(item_id)).first()
        if item:
            session.delete(item)
            session.commit()
            resequence_ids()
            ui.notify(f'Item with ID {item_id} deleted successfully!', color='green')
        else:
            ui.notify(f'Item with ID {item_id} not found.', color='red')
    except ValueError:
        ui.notify('Invalid ID format.', color='red')

def create_nicegui_ui():
    global global_table

    with ui.card().style('width: 500px; padding: 16px'):
        ui.label('Add Item')
        name = ui.input(label='Item Name').classes('q-mb-md')
        password = ui.input(label='Password').classes('q-mb-md').props('type=password')
        ui.button('Submit', on_click=lambda: add_item(name.value, password.value))

    with ui.card().style('width: 600px; padding: 16px'):
        ui.label('Items List')
        global_table = ui.table(
            columns=[
                {'name': 'ID', 'label': 'ID', 'field': 'ID'},
                {'name': 'Name', 'label': 'Name', 'field': 'Name'},
                {'name': 'Password', 'label': 'Password', 'field': 'Password'}
            ],
            rows=[],
            row_key='ID'
        )
        ui.button('Refresh', on_click=refresh_items_list)

    with ui.card().style('width: 600px; padding: 16px'):
        delete_id = ui.input(label='ID to delete').classes('q-mb-md')
        ui.button('Delete', on_click=lambda: delete_item(delete_id.value))

if __name__ in {"__main__", "__mp_main__"}:
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    
    create_nicegui_ui()
    ui.run(title="SQLAlchemy + Alembic Example")
