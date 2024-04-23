from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlite3 import IntegrityError


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
    # numRedPotions = 0
    # numGreenPotions = 0
    # numBluePotions = 0

    # potion = potions_delivered[0]
    # if potion.potion_type == [100, 0, 0, 0]:
    #     numRedPotions += potion.quantity
    # elif potion.potion_type == [0, 100, 0, 0]:
    #     numGreenPotions += potion.quantity
    # elif potion.potion_type == [0, 0, 100, 0]:
    #     numBluePotions += potion.quantity
    
    with db.engine.begin() as connection:
        try: 
            redPotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE name = 'CRANBERRY_red'"))
            redPotion = redPotion.fetchone()
            greenPotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE name = 'ELF_green'"))
            greenPotion = greenPotion.fetchone()
            bluePotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE name = 'STITCH_blue'"))
            bluePotion = bluePotion.fetchone()
            purplePotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE name = 'GRIMACE_purple'"))
            purplePotion = purplePotion.fetchone()
        except IntegrityError:
            return "Integrity Error"
        else:
            newPotion = potions_delivered[0].potion_type
            #code for red potion
            if newPotion == [redPotion.redPot, redPotion.greenPot, redPotion.bluePot, redPotion.blackPot]: 
                    connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions + :potions, num_red_ml = num_red_ml - (100 * :potions)"), {"potions": newPotion.quantity})

                    
            #code for green potion
            if newPotion == [greenPotion.redPot, greenPotion.greenPot, greenPotion.bluePot, greenPotion.blackPot]: 
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + :potions, num_green_ml = num_green_ml - (100 * :potions)"), {"potions": newPotion.quantity})

           
            #blue potion
            if newPotion == [bluePotion.redPot, bluePotion.greenPot, bluePotion.bluePot, bluePotion.blackPot]: 
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = num_blue_potions + :potions, num_blue_ml = num_blue_ml - (100 * :potions)"), {"potions": newPotion.quantity})
            #purple potion
            if newPotion == [purplePotion.redPot, purplePotion.greenPot, purplePotion.bluePot, purplePotion.blackPot]:  
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_purple_potions = num_purple_potions + :potions, num_red_ml = num_red_ml - (50 * :potions), num_blue_ml = num_blue_ml - (50 * :potions)"), {"potions": newPotion.quantity})
    
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
        SELECT * FROM global_inventory
        """

        result = connection.execute(sqlalchemy.text(sql_to_execute))
        firstRow = result.first()


    
        redPots = firstRow.num_red_ml // 100
        greenPots = firstRow.num_green_ml // 100
        bluePots = firstRow.num_green_ml // 100
        if firstRow.num_red_ml >= 50 and firstRow.num_green_ml >= 50:
            purplePotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE name = 'GRIMACE_purple'"))
            myPurplePotion = purplePotion.fetchone()
            return [
                {
                    "potion_type": [myPurplePotion.redPot, myPurplePotion.greenPot, myPurplePotion.bluePot, myPurplePotion.blackPot],
                    "quantity": 1
                }
            ]
        #return number of potions. if num_green_ml == 0, potionQuantity will be 0
        if redPots != 0:
            redPotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE name = 'CRANBERRY_red'"))
            myRedPotion = redPotion.fetchone()
            return [
                {
                    "potion_type": [myRedPotion.redPot, myRedPotion.greenPot, myRedPotion.bluePot, myRedPotion.blackPot],
                    "quantity": redPots
                }
            ]
        if greenPots != 0:
            greenPotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE name = 'ELF_green'"))
            myGreenPotion = greenPotion.fetchone()
            return [
                {
                    "potion_type": [myGreenPotion.redPot, myGreenPotion.greenPot, myGreenPotion.bluePot, myGreenPotion.blackPot],
                    "quantity": greenPots
                }
            ]
        if bluePots != 0:
            bluePotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE name = 'STITCH_blue'"))
            myBluePotion = bluePotion.fetchone()
            return [
                {
                    "potion_type": [myBluePotion.redPot, myBluePotion.greenPot, myBluePotion.bluePot, myBluePotion.blackPot],
                    "quantity": bluePots
                }
            ]
        return []

if __name__ == "__main__":
    print(get_bottle_plan())