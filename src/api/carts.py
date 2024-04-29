from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db



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

#carts = {}
#global_cart_id = 0
@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    # Add Customer info to new row in carts table
    # Return the id of that row
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""INSERT INTO carts (customer_name, character_class, level) 
                                           VALUES (:x, :y, :z)
                                           RETURNING id"""),
                                           [{"x": new_cart.customer_name, "y": new_cart.character_class, "z": new_cart.level}])
        cart_id = result.scalar_one()
    return {"cart_id": cart_id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    #carts[cart_id] = (item_sku, cart_item.quantity)
    # Add cart item info to a new row with respect to foreign keys of cart_id and item_sku
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""INSERT INTO cart_items (cart_id, quantity, potion_sku)
                                        VALUES (:x, :y, :z)"""),[{"x": cart_id, "y": cart_item.quantity, "z": item_sku}]) 
    return "OK"

#
class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    total_potions = 0
    total_gold = 0
    # Use the info between tables to write an efficient checkout process (quantity, cost, )
    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar_one()
        item_results = connection.execute(sqlalchemy.text("""SELECT 
                                                     cart_id, 
                                                     quantity, 
                                                     potion_sku
                                                     FROM cart_items WHERE cart_items.cart_id = :x"""),[{"x": cart_id}])
        for row in item_results:
            pot_type = connection.execute(sqlalchemy.text("""SELECT type 
                                                        FROM potions
                                                        WHERE potions.sku = :x"""),[{"x": row.potion_sku}]).scalar_one()
            connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_type, change, description) 
                                        VALUES (:x, :y, :z)"""),
                                        [{"x": pot_type, "y": -row.quantity, "z": "Potion Sold"}])
            price = connection.execute(sqlalchemy.text("""SELECT price 
                                                        FROM potions
                                                        WHERE potions.sku = :x"""),[{"x": row.potion_sku}]).scalar_one()
            gold += price*row.quantity
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :x"),[{"x": gold}])

            curr_inventory = connection.execute(sqlalchemy.text("""SELECT inventory FROM potions 
                                                                WHERE potions.sku = :x"""),[{"x": row.potion_sku}]).scalar_one()
            connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x 
                                                WHERE potions.sku = :y"""),[{"x": (curr_inventory - row.quantity), "y": row.potion_sku}])
            total_potions += row.quantity
            total_gold += price*row.quantity
        
        connection.execute(sqlalchemy.text("""INSERT INTO gold_ledger (change, description) 
                                           VALUES (:x, :y)"""),
                                           [{"x":  total_gold, "y": "Barrels Purchased"}])
        

  

    return {"total_potions_bought": total_potions, "total_gold_paid": total_gold}
