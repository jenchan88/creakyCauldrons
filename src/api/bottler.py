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
            redPotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE potname = 'CRANBERRY_red'"))
            redPotion = redPotion.fetchone()
            greenPotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE potname = 'ELF_green'"))
            greenPotion = greenPotion.fetchone()
            bluePotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE potname = 'STITCH_blue'"))
            bluePotion = bluePotion.fetchone()
            purplePotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE potname = 'GRIMACE_purple'"))
            purplePotion = purplePotion.fetchone()
        except IntegrityError:
            return "Integrity Error"
        else:
            newPotionType = potions_delivered[0].potion_type
            newPotionQuant = potions_delivered[0].quantity
            #code for red potion
            if newPotionType == [redPotion.redpot, redPotion.greenpot, redPotion.bluepot, redPotion.blackpot]: 
                    sql_to_execute = "INSERT INTO ledger (gold, potions, numbml, potionType, descrip) VALUES (0, :potions, -:numbml, 1, 'bottling 1 red potion')"
                    connection.execute(sqlalchemy.text(sql_to_execute), {"potions": newPotionQuant, "numbml": 100*newPotionQuant})

                    
            #code for green potion
            if newPotionType == [greenPotion.redpot, greenPotion.greenpot, greenPotion.bluepot, greenPotion.blackpot]: 
                sql_to_execute = "INSERT INTO ledger (gold, potions, numbml, potionType, descrip) VALUES (0, :potions, -:numbml, 3, 'bottling 1 green potion')"
                connection.execute(sqlalchemy.text(sql_to_execute), {"potions": newPotionQuant, "numbml": 100*newPotionQuant})
                
           
            #blue potion
            if newPotionType == [bluePotion.redpot, bluePotion.greenpot, bluePotion.bluepot, bluePotion.blackpot]: 
                sql_to_execute = "INSERT INTO ledger (gold, potions, numbml, potionType, descrip) VALUES (0, :potions, -:numbml, 4, 'bottling 1 blue potion')"
                connection.execute(sqlalchemy.text(sql_to_execute), {"potions": newPotionQuant, "numbml": 100*newPotionQuant})
            #purple potion
            if newPotionType == [purplePotion.redpot, purplePotion.greenpot, purplePotion.bluepot, purplePotion.blackpot]:  
                sql_to_execute = "INSERT INTO ledger (gold, potions, numbml, potionType, descrip) VALUES (0, :potions, -:numbml, 2, 'bottling 1 purple potion')"
                connection.execute(sqlalchemy.text(sql_to_execute), {"potions": newPotionQuant, "numbml": 100*newPotionQuant})

                #for red and blue comps making purple
                sql_to_execute = "INSERT INTO ledger (gold, potions, numbml, potionType, descrip) VALUES (0, 0, -:numbml, 1, 'red part of purple potion')"
                connection.execute(sqlalchemy.text(sql_to_execute), {"numbml": 50 *newPotionQuant})

                sql_to_execute = "INSERT INTO ledger (gold, potions, numbml, potionType, descrip) VALUES (0, 0, -:numbml, 4, 'blue part of purple potion')"
                connection.execute(sqlalchemy.text(sql_to_execute), {"numbml": 50 *newPotionQuant})

                
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
        # sql_to_execute = """
        # SELECT * FROM global_inventory
        # """

        # result = connection.execute(sqlalchemy.text(sql_to_execute))
        #potions = connection.execute(sqlalchemy.text("SELECT * from potionOfferings"))
        # firstRow = result.first()

        try:
            sql_to_execute = "SELECT COALESCE(SUM(numbml), 0) FROM ledger WHERE potiontype = 1"
            redMils = connection.execute(sqlalchemy.text(sql_to_execute)).first()

            sql_to_execute = "SELECT COALESCE(SUM(numbml), 0) FROM ledger WHERE potiontype = 3"
            greenMils = connection.execute(sqlalchemy.text(sql_to_execute)).first()

            sql_to_execute = "SELECT COALESCE(SUM(numbml), 0) FROM ledger WHERE potiontype = 4"
            blueMils = connection.execute(sqlalchemy.text(sql_to_execute)).first()

            sql_to_execute = "SELECT COALESCE(SUM(numbml), 0) FROM ledger WHERE potiontype = 2"
            purpleMils = connection.execute(sqlalchemy.text(sql_to_execute)).first()

        except IntegrityError:
            return "integrity error"    

        num_red_ml = redMils[0]
        num_green_ml = greenMils[0]
        num_blue_ml = blueMils[0]
        num_pur_ml = purpleMils[0]
    
        # redPots = firstRow.num_red_ml // 100
        # greenPots = firstRow.num_green_ml // 100
        # bluePots = firstRow.num_green_ml // 100


        if num_red_ml >= 50 and num_blue_ml >= 50:
            #purple logic
    
            purplePotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE potname = 'GRIMACE_purple'"))
            myPurplePotion = purplePotion.fetchone()
            return [
                {
                    "potion_type": [myPurplePotion.redpot, myPurplePotion.greenpot, myPurplePotion.bluepot, myPurplePotion.blackpot],
                    "quantity": 1
                }
            ]
        #return number of potions. if num_green_ml == 0, potionQuantity will be 0
        elif num_red_ml >= 100:
            redPotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE potname = 'CRANBERRY_red'"))
            myRedPotion = redPotion.fetchone()
            return [
                {
                    "potion_type": [myRedPotion.redpot, myRedPotion.greenpot, myRedPotion.bluepot, myRedPotion.blackpot],
                    "quantity": 1
                }
            ]
        if num_green_ml >= 100:
            greenPotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE potname = 'ELF_green'"))
            myGreenPotion = greenPotion.fetchone()
            return [
                {
                    "potion_type": [myGreenPotion.redpot, myGreenPotion.greenpot, myGreenPotion.bluepot, myGreenPotion.blackpot],
                    "quantity": 1
                }
            ]
        if num_blue_ml >= 100:
            bluePotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE potname = 'STITCH_blue'"))
            myBluePotion = bluePotion.fetchone()
            return [
                {
                    "potion_type": [myBluePotion.redpot, myBluePotion.greenpot, myBluePotion.bluepot, myBluePotion.blackpot],
                    "quantity": 1
                }
            ]
        return []

if __name__ == "__main__":
    print(get_bottle_plan())