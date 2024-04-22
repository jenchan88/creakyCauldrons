from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    availPotions = []
    with db.engine.begin() as connection:
        sql_to_execute = """
        SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory
        """

        result = connection.execute(sqlalchemy.text(sql_to_execute))
    firstRow = result.first()
    if(firstRow.num_red_potions > 0):
        availPotions.append(
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": firstRow.num_red_potions,
                "price": 50,
                "potion_type": [100, 0, 0, 0]
            }
        )
    if(firstRow.num_green_potions > 0):
        availPotions.append(
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": firstRow.num_green_potions,
                "price": 50,
                "potion_type": [0, 100, 0, 0]
            }
        )
    if(firstRow.num_blue_potions > 0):
        availPotions.append(
            {
                "sku": "BLUE_POTION_0",
                "name": "blue potion",
                "quantity": firstRow.num_blue_potions,
                "price": 50,
                "potion_type": [0, 0, 100, 0]
            }
        )
    return availPotions

    