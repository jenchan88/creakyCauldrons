from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")
    numRedPotions = 0
    numGreenPotions = 0
    numBluePotions = 0

    potion = potions_delivered[0]
    if potion.potion_type == [100, 0, 0, 0]:
        numRedPotions += potion.quantity
    elif potion.potion_type == [0, 100, 0, 0]:
        numGreenPotions += potion.quantity
    elif potion.potion_type == [0, 0, 100, 0]:
        numBluePotions += potion.quantity
    
    with db.engine.begin() as connection:
        sql_to_execute = f"""UPDATE global_inventory 
                            SET num_red_potions = num_red_potions + {numRedPotions}, 
                            num_red_ml = num_red_ml - ({numRedPotions}*100),
                            num_green_potions = num_green_potions + {numGreenPotions},
                            num_green_ml = num_green_ml - ({numGreenPotions}*100), 
                            num_blue_potions = num_blue_potions + {numBluePotions},
                            num_blue_ml = num_blue_ml - ({numBluePotions}*100)"""

        connection.execute(sqlalchemy.text(sql_to_execute))
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    with db.engine.begin() as connection:
        sql_to_execute = """
        SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory
        """

        result = connection.execute(sqlalchemy.text(sql_to_execute))
    
    redPots = (result.first()).num_red_ml // 100
    greenPots = (result.first()).num_green_ml // 100
    bluePots = (result.first()).num_blue_ml // 100
  
    #return number of potions. if num_green_ml == 0, potionQuantity will be 0
    if redPots > 0:
        return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": redPots
            }
        ]
    elif greenPots > 0:
        return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": greenPots
            }
        ]
    elif bluePots > 0:
        return [
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": bluePots
            }
        ]
    return []

if __name__ == "__main__":
    print(get_bottle_plan())