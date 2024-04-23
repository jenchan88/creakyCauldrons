from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlite3 import IntegrityError

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
    

    with db.engine.begin() as connection:
        try:
            if barrels_delivered:
                barrel = barrels_delivered[0]
                column = None
                
                if barrel.sku == "SMALL_RED_BARREL":
                    column = "num_red_ml"
                elif barrel.sku == "SMALL_GREEN_BARREL":
                    column = "num_green_ml"
                elif barrel.sku == "SMALL_BLUE_BARREL":
                    column = "blue_ml"
                #update global_inventory
                if column:
                    sql_to_execute = f"""
                    UPDATE global_inventory SET gold = gold - :gold, {column} = {column} + :ml
                    """
                    connection.execute(sqlalchemy.text(sql_to_execute), {"gold": barrel.price, "ml": barrel.ml_per_barrel})
        except IntegrityError:
            return "Integrity Error"
    return "OK"
    
    
    
# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    small_barrel_skus = {"SMALL_BLUE_BARREL", "SMALL_RED_BARREL", "SMALL_GREEN_BARREL"}

    print(wholesale_catalog)
    with db.engine.begin() as connection:
        sql_to_execute = """
        SELECT gold FROM global_inventory
        """

        result = connection.execute(sqlalchemy.text(sql_to_execute))
        firstRow = result.first()
    
    
    if firstRow is None:
        print("can't find gold")
        return []
    totalGold = firstRow.gold

    plan = []
    for barrel in wholesale_catalog:
        
        if barrel.sku in small_barrel_skus:
            #can't afford this barrel, move to next one
            if totalGold < barrel.price:
                continue
            
            plan.append({
                "sku": barrel.sku,
                "quantity": 1
            })
            return plan
    return plan
  