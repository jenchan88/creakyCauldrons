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
    totalRed = 0
    totalGreen = 0
    totalBlue = 0
    totalCost = 0

        
    barrel = barrels_delivered[0]
    totalCost += barrel.price
    if barrel.sku == "SMALL_RED_BARREL":
        totalRed += barrel.ml_per_barrel
    elif barrel.sku == "SMALL_GREEN_BARREL":
        totalGreen += barrel.ml_per_barrel
    elif barrel.sku == "SMALL_BLUE_BARREL":
        totalBlue += barrel.ml_per_barrel
    
    
    with db.engine.begin() as connection:
        sql_to_execute = f"""UPDATE global_inventory 
                            SET gold = gold - {totalCost}, 
                            num_red_ml = num_red_ml + {totalRed}, 
                            num_green_ml = num_green_ml + {totalGreen}, 
                            num_blue_ml = num_blue_ml + {totalBlue}"""
        connection.execute(sqlalchemy.text(sql_to_execute))
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    with db.engine.begin() as connection:
        sql_to_execute = """
        SELECT num_red_potions, num_green_potions, num_blue_potions, gold FROM global_inventory
        """

        result = connection.execute(sqlalchemy.text(sql_to_execute))
    firstRow = result.first()
    totalGold = firstRow.gold
    
    
    if (totalGold >= 100 and firstRow.num_red_potions < 5):

        return [
            {            
                "sku": "SMALL_RED_BARREL",
                "quantity": 1
            }
        ]
    elif (totalGold >= 100 and firstRow.num_green_potions < 5):

        return [
            {            
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1
            }
        ]
    elif (totalGold >= 120 and firstRow.num_blue_potions < 5):

        return [
            {            
                "sku": "SMALL_BLUE_BARREL",
                "quantity": 1
            }
        ]

    return []

