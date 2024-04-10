from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    totExpenses = 0
    totGreenMl = 0

    for barrel in barrels_delivered:
        totExpenses += barrel.price
        totGreenMl += barrel.ml_per_barrel

    with db.engine.begin() as connection:
        sql_to_execute = "UPDATE global_inventory SET gold=gold-{totExpenses},num_green_ml=num_green_ml+{totGreenMl}"

        connection.execute(sqlalchemy.text(sql_to_execute))
    return "OK"
    
# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT num_green_potions, gold FROM global_inventory"

        result = connection.execute(sqlalchemy.text(sql_to_execute))
    firstRow = result.first()
    for barrel in wholesale_catalog:
        if barrel.sku == "SMALL_GREEN_BARREL":
            if (firstRow.gold >= barrel.price) and (firstRow.num_green_potions < 10):
    
                return [
                    {
                        
                        "sku": "SMALL_GREEN_BARREL",
                        "quantity": 1
                    }
                ]
            else:
                return []

