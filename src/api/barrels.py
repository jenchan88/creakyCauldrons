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
                potType = 0
                message = None
                
                if barrel.sku == "SMALL_RED_BARREL":
                    column = "num_red_ml"
                    potType = 1
                    message = "buying 1 small red barrel"
                elif barrel.sku == "SMALL_GREEN_BARREL":
                    column = "num_green_ml"
                    potType = 3
                    message = "buying 1 small green barrel"
                elif barrel.sku == "SMALL_BLUE_BARREL":
                    column = "blue_ml"
                    potType = 4
                    message = "buying 1 small blue barrel"
                #update global_inventory
                if column:
                    sql_to_execute = f"""
                    INSERT into ledger (gold, numbml, potions, potiontype, descrip) VALUES (-:gold, 0, :numbml, :potType, :descrip) 
                    """
                    connection.execute(sqlalchemy.text(sql_to_execute), {"gold": barrel.price, "numbml": barrel.ml_per_barrel, "potiontype":potType, "descrip":message})
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
        try:
            
            sql_to_execute = """
            SELECT SUM(gold) FROM ledger
            """

            result = connection.execute(sqlalchemy.text(sql_to_execute))
            firstRow = result.first()
            if firstRow is None:
                print("can't find gold")
                return []
            totalGold = firstRow.gold
        except IntegrityError:
            return "INTEGRITY ERROR!"
    

    plan = []
    for barrel in wholesale_catalog:
        
        if barrel.sku in small_barrel_skus:
            #can't afford this barrel, move to next one
            if totalGold <= barrel.price:
                continue
            
            plan.append({
                "sku": barrel.sku,
                "quantity": 1
            })
            return plan
    return plan
  