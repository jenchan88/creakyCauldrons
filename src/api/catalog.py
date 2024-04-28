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
        potion_types = {
            "Cranberry_red": ("num_red_potions", "SELECT * FROM potionOfferings WHERE name = 'Cranberry_red'"),
            "ELF_green": ("num_green_potions", "SELECT * FROM potionOfferings WHERE name = 'ELF_green'"),
            "STITCH_blue": ("blue_potions", "SELECT * FROM potionOfferings WHERE name = 'STITCH_blue'"),
            "GRIMACE_purple": ("num_purple_potions", "SELECT * FROM potionOfferings WHERE name = 'GRIMACE_purple'")
        }

        sql_to_execute = """SELECT * FROM global_inventory"""
        inventory = connection.execute(sqlalchemy.text(sql_to_execute))
        inven = inventory.first()
        redPotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE name = 'Cranberry_red'"))
        redPotion = redPotion.first()
        bluePotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE name = 'ELF_green'"))
        bluePotion = bluePotion.first()
        greenPotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE name = 'STITCH_blue'"))
        greenPotion = greenPotion.first()
        purplePotion = connection.execute(sqlalchemy.text("SELECT * FROM potionOfferings WHERE name = 'GRIMACE_purple'"))
        purPotion = purplePotion.first()

        if inven.num_red_potions > 0:
            catalog.append({
                "sku": redPotion.potName,
                    "name": redPotion.potName, 
                    "quantity": inven.num_red_potions,
                    "price": redPotion.price,
                    "potion_type": [redPotion.redPot, redPotion.greenPot, redPotion.bluePot, redPotion.blackPot]
            })
        if inven.num_green_potions > 0:
            catalog.append({
                "sku": greenPotion.potName,
                    "name": greenPotion.potName,
                    "quantity": inven.num_green_potions,
                    "price": greenPotion.price,
                    "potion_type": [greenPotion.redPot, greenPotion.greenPot, greenPotion.bluePot, greenPotion.blackPot]
            })
        if inven.num_blue_potions > 0:
            catalog.append({
                "sku": bluePotion.potName,
                    "name": bluePotion.potName,
                    "quantity": inven.num_blue_potions,
                    "price": bluePotion.price,
                    "potion_type": [bluePotion.redPot, bluePotion.greenPot, bluePotion.bluePot, bluePotion.blackPot]
            })
        if inven.num_purple_potions > 0:
            catalog.append({
                "sku": purPotion.potName,
                    "name": purPotion.potName,
                    "quantity": inven.num_purple_potions,
                    "price": purPotion.price,
                    "potion_type": [purPotion.redPot, purPotion.greenPot, purPotion.bluePot, purPotion.blackPot]
            })
        
        
    
    return catalog


    