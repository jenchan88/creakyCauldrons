from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    with db.engine.begin() as connection:
        # sql_to_execute = """UPDATE global_inventory SET gold = 100, num_red_potions = 0, num_red_ml = 0, num_green_potions = 0, num_green_ml = 0, num_blue_potions = 0, num_blue_ml = 0"""

        # connection.execute(sqlalchemy.text(sql_to_execute))

        connection.execute(sqlalchemy.text("DELETE FROM ledger"))
        connection.execute(sqlalchemy.text("DELETE FROM cart_items"))
        connection.execute(sqlalchemy.text("DELETE FROM carts_table"))
        connection.execute(sqlalchemy.text("INSERT INTO ledger (gold, descrip) VALUES (100, 'reset')"))

    return "OK"

