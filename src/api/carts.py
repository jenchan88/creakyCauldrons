from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db
from fastapi import HTTPException
from sqlite3 import IntegrityError



router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    # global cartIDCount
    # cartIDCount += 1
    # return {"cart_id": cartIDCount}

    sql_to_execute ="""
                    INSERT INTO carts_table (customer_name) VALUES (:name) returning cart_id
                    """
    with db.engine.begin() as connection:
        try:
            cart_id = connection.execute(sqlalchemy.text(sql_to_execute), {"name": new_cart.customer_name}).scalar_one()
        except IntegrityError:
            return "Integrity Error"
      
    return {"cart_id": cart_id}

class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    # global cart
    # cart = {}
    # cart[cart_id] = (item_sku, cart_item.quantity)
    print(f"set item quantity {cart_id} {item_sku}")
    total_potions = 0
    with db.engine.begin() as connection:
        try:
            sql_to_execute = """
            SELECT COALESCE(
                (SELECT SUM(potions) FROM ledger WHERE potiontype = :potion_type), 0
            ) AS total_potions
            """
            if item_sku == "CRANBERRY_red":
                total_potions = connection.execute(sqlalchemy.text(sql_to_execute), {"potion_type": 1}).scalar_one()
                
                print(f"Total potions for potion type 1: {total_potions}")
            elif item_sku == "ELF_green":
                total_potions = connection.execute(sqlalchemy.text(sql_to_execute), {"potion_type": 3}).scalar_one()
                
                print(f"Total potions for potion type 3: {total_potions}")
            elif item_sku == "STITCH_blue":
                total_potions = connection.execute(sqlalchemy.text(sql_to_execute), {"potion_type": 4}).scalar_one()
                
                print(f"Total potions for potion type 4: {total_potions}")

            elif item_sku == "GRIMACE_purple":
                total_potions = connection.execute(sqlalchemy.text(sql_to_execute), {"potion_type": 2}).scalar_one()
                
                print(f"Total potions for potion type 2: {total_potions}")
                
            if total_potions is not None:
                sql_to_execute ="""
                    SELECT potid FROM potionOfferings WHERE potname = :name
                    """
                    
                potionID = connection.execute(sqlalchemy.text(sql_to_execute), {"name": item_sku}).scalar_one()
            else:
                return HTTPException("No potion found")
            # sql_to_execute ="""
            #         SELECT potid FROM potionOfferings WHERE potname = :name
            #         """
                    
            # potionID = connection.execute(sqlalchemy.text(sql_to_execute), {"name": item_sku}).scalar_one()
            print(f"found potion {potionID}")
            
            
            sql_to_execute ="""
                    INSERT INTO cart_items (cart_id, pot_type, amount) VALUES (:cart_id, :potion_id, :quantity)
                    """
            connection.execute(sqlalchemy.text(sql_to_execute), {"cart_id": cart_id, "potion_id": potionID, "quantity": cart_item.quantity})
        except IntegrityError:
            return "Integrity Error"
    
    return "OK"

class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
        try:
    

            sql_to_execute = """
                            SELECT pot_type, amount FROM cart_items WHERE cart_id = :cart_id
                            """
            result = connection.execute(sqlalchemy.text(sql_to_execute), {"cart_id": cart_id})
            firstRow = result.first()
            potType = firstRow[0]
            print(firstRow)
            print("potion type: ", potType)
            quant = firstRow[1]
            
            sql_to_execute = """
                            SELECT potname, price FROM potionOfferings WHERE potid = :potType
                            """
            result = connection.execute(sqlalchemy.text(sql_to_execute), [{"potType": potType}])
            potion = result.first()
            curPotName = potion[0]
            totalCost = potion[1]
                
        # sql_to_execute = f"""UPDATE global_inventory 
        #                             SET num_red_potions = num_red_potions - {numPotions}, 
        #                             gold=gold+({numPotions}* 50)"""
                
                # Define prices and update global_inventory accordingly
            # potion_prices = {"CRANBERRY_red": 20, "ELF_green": 30, "STITCH_blue": 40, "GRIMACE_purple": 50}
            
            # if  curPotName in potion_prices:
            #     price_per_potion = potion_prices[curPotName]
            #     if curPotName.endswith("_red"):
            #         color_column = "num_red_potions"
            #     elif curPotName.endswith("_green"):
            #         color_column = "num_green_potions"
            #     elif curPotName.endswith("_blue"):
            #         color_column = "num_blue_potions"
            #     elif curPotName.endswith("_purple"):
            #         color_column = "num_purple_potions"
            #     else:
            #         return "Invalid potion name"p

        #         connection.execute(
        #     sqlalchemy.text(f"UPDATE global_inventory SET {color_column} = {color_column} - :potions, gold = gold + :total_gold"),
        #     {"potions": quant, "total_gold": price_per_potion * quant}
        # )
        #     totalGoldPaid = price_per_potion * quant
        # sql_to_execute = f"""
        # UPDATE potionOfferings SET quantselling = quantselling - :potions WHERE potid = :potType
        # """

            sql_to_execute = """
                                INSERT INTO ledger (gold, potions, numbml, potiontype, descrip) VALUES (:cost, -:potions, 0, :potionType, 'sold potion')
                                """
            connection.execute(sqlalchemy.text(sql_to_execute), {"cost": totalCost, "potionType": potType, "potions": quant})
            totalGoldPaid = totalCost * quant
        except IntegrityError:
            return "Integrity Error"
        

    return {"total_potions_bought": quant, "total_gold_paid": totalGoldPaid}
