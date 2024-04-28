from fastapi import APIRouter
import sqlalchemy
from src import database as db
from sqlite3 import IntegrityError

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    catalog = []
    with db.engine.begin() as connection:
        # potion_types = {
        #     "CRANBERRY_red": ("num_red_potions", "SELECT * FROM potionOfferings WHERE potname = 'CRANBERRY_red'"),
        #     "ELF_green": ("num_green_potions", "SELECT * FROM potionOfferings WHERE potname = 'ELF_green'"),
        #     "STITCH_blue": ("blue_potions", "SELECT * FROM potionOfferings WHERE potname = 'STITCH_blue'"),
        #     "GRIMACE_purple": ("num_purple_potions", "SELECT * FROM potionOfferings WHERE potname = 'GRIMACE_purple'")
        # }

        sql_to_execute = """SELECT * FROM global_inventory"""
        inventory = connection.execute(sqlalchemy.text(sql_to_execute))
        inven = inventory.first()
        redPotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE potname = 'CRANBERRY_red'"))
        redPotion = redPotion.first()
        bluePotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE potname = 'ELF_green'"))
        bluePotion = bluePotion.first()
        greenPotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE potname = 'STITCH_blue'"))
        greenPotion = greenPotion.first()
        purplePotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE potname = 'GRIMACE_purple'"))
        purPotion = purplePotion.first()

        if inven.num_red_potions > 0:
            catalog.append({
                "sku": redPotion.potname,
                    "name": redPotion.potname,  
                    "quantity": inven.num_red_potions,
                    "price": redPotion.price,
                    "potion_type": [redPotion.redpot, redPotion.greenpot, redPotion.bluepot, redPotion.blackpot]
            })
        if inven.num_green_potions > 0:
            catalog.append({
                "sku": greenPotion.potname,
                    "name": greenPotion.potname,
                    "quantity": inven.num_green_potions,
                    "price": greenPotion.price,
                    "potion_type": [greenPotion.redpot, greenPotion.greenpot, greenPotion.bluepot, greenPotion.blackpot]
            })
        if inven.num_blue_potions > 0:
            catalog.append({
                "sku": bluePotion.potname,
                    "name": bluePotion.potname,
                    "quantity": inven.num_blue_potions,
                    "price": bluePotion.price,
                    "potion_type": [bluePotion.redpot, bluePotion.greenpot, bluePotion.bluepot, bluePotion.blackpot]
            })
        if inven.num_purple_potions > 0:
            catalog.append({
                "sku": purPotion.potname,
                    "name": purPotion.potname,
                    "quantity": inven.num_purple_potions,
                    "price": purPotion.price,
                    "potion_type": [purPotion.redpot, purPotion.greenpot, purPotion.bluepot, purPotion.blackpot]
            })
        
        
    
    return catalog


    