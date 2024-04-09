from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        sql_to_execute = "SELECT num_green_potions FROM global_inventory"

        result = connection.execute(sqlalchemy.text(sql_to_execute))
    firstRow = result.first()
    if(firstRow.num_green_potions > 0):
        return [
                {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": 1,
                    "price": 50,
                    "potion_type": [0, 100, 0, 0],
                }
            ]
    else:
        return [{
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": 0,
                    "price": 50,
                    "potion_type": [0, 100, 0, 0],
                }

        ]
    

    