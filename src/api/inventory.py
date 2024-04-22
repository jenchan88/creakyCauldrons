from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        sql_to_execute = """SELECT * FROM global_inventory"""
        result = connection.execute(sqlalchemy.text(sql_to_execute))
    firstRow = result.first()
    #return {"number_of_potions": 0, "ml_in_barrels": 0, "gold": 0}
    return {"red_potions": firstRow.num_red_potions, "red_ml": firstRow.num_red_ml,"green_potions": firstRow.num_green_potions, "green_ml": firstRow.num_green_ml, "gold": firstRow.gold, "blue_potions": firstRow.num_blue_potions, "blue_ml": firstRow.num_blue_potions}
# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
