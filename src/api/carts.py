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

    if sort_col is search_sort_options.customer_name:
        order_by = db.search_view.c.customer_name
    elif sort_col is search_sort_options.item_sku:
        order_by = db.search_view.c.potion_sku
    elif sort_col is search_sort_options.line_item_total:
        order_by = db.search_view.c.cost
    else:
        order_by = db.search_view.c.created_at

    if sort_order == search_sort_order.asc:
        order_by = order_by.asc()
    else:
        order_by = order_by.desc()

    if search_page == "":
        offset = 0
    else:
        offset = int(search_page)

    with db.engine.begin() as connection:
        count = connection.execute(sqlalchemy.text("""SELECT COUNT(*) FROM search_view""")).scalar_one()
    
    offset_max = count//5
    print(offset_max)

    stmt = (
        sqlalchemy.select(
            db.search_view.c.cart_item_id,
            db.search_view.c.customer_name,
            db.search_view.c.potion_sku,
            db.search_view.c.cost,
            db.search_view.c.created_at,
            db.search_view.c.quantity,
        )
        .limit(6)
        .offset(offset*5)
        .order_by(order_by)
    )
    if customer_name != "":
        stmt = stmt.where(db.search_view.c.customer_name.ilike(f"%{customer_name}%"))
    if potion_sku != "":
        stmt = stmt.where(db.search_view.c.potion_sku.ilike(f"%{potion_sku}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                "line_item_id": row.cart_item_id,
                "item_sku": f"{row.quantity} {row.potion_sku}",
                "customer_name": row.customer_name,
                "line_item_total": row.cost,
                "timestamp": row.created_at,
            }
            )
    if offset - 1 < 0:
        previous = ""
    else:
        previous = str(offset-1)
    if len(json) < 6:
        next = ""
    else:
        next = str(offset+1)

    return {
        "previous": previous,
        "next": next,
        "results": json[:5],
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
    with db.engine.begin() as connection:
        price = connection.execute(sqlalchemy.text("""SELECT price 
                                                        FROM potions
                                                        WHERE potions.sku = :x"""),[{"x": item_sku}]).scalar_one()
        connection.execute(sqlalchemy.text("""INSERT INTO cart_items (cart_id, quantity, potion_sku, cost)
                                        VALUES (:x, :y, :z, :q)"""),[{"x": cart_id, "y": cart_item.quantity, "z": item_sku, "q": price*cart_item.quantity}]) 
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    total_potions = 0
    total_gold = 0
    with db.engine.begin() as connection:
        item_results = connection.execute(sqlalchemy.text("""SELECT 
                                                     cart_id, 
                                                     quantity, 
                                                     potion_sku, 
                                                     cost 
                                                     FROM cart_items WHERE cart_items.cart_id = :x"""),[{"x": cart_id}])
        for row in item_results:
            pot_type = connection.execute(sqlalchemy.text("""SELECT type 
                                                        FROM potions
                                                        WHERE potions.sku = :x"""),[{"x": row.potion_sku}]).scalar_one()
            connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_type, change, description) 
                                        VALUES (:x, :y, :z)"""),
                                        [{"x": pot_type, "y": -row.quantity, "z": "Potion Sold"}])
            # price = connection.execute(sqlalchemy.text("""SELECT price 
            #                                             FROM potions
            #                                             WHERE potions.sku = :x"""),[{"x": row.potion_sku}]).scalar_one()

            inventory = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS potion_tot 
                                                                FROM potion_ledger
                                                                WHERE potion_type = :x"""),[{"x": pot_type}]).scalar_one()
            connection.execute(sqlalchemy.text("""UPDATE potions SET inventory = :x 
                                                WHERE potions.sku = :y"""),[{"x": (inventory), "y": row.potion_sku}])
            total_potions += row.quantity
            total_gold += row.cost
        
        connection.execute(sqlalchemy.text("""INSERT INTO gold_ledger (change, description) 
                                           VALUES (:x, :y)"""),
                                           [{"x":  total_gold, "y": "Potion Sold"}])
        

  

    return {"total_potions_bought": total_potions, "total_gold_paid": total_gold}
