from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db




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
        connection.execute(sqlalchemy.text("""INSERT INTO barrel_orders (id, description) 
                                           VALUES (:x, :y)"""),
                                           [{"x": order_id, "y": "New Barrel Order"}])
        for barrel in barrels_delivered:
            connection.execute(sqlalchemy.text("""INSERT INTO barrel_order_items (sku, ml_per_barrel, potion_type, price, quantity, order_id) 
                                           VALUES (:x, :y, :z, :w, :q, :p)"""),
                                           [{"x": barrel.sku, "y": barrel.ml_per_barrel, "z": barrel.potion_type, "w": barrel.price, "q": barrel.quantity, "p": order_id}])
            connection.execute(sqlalchemy.text("""INSERT INTO ml_ledger (potion_type, change, description) 
                                           VALUES (:x, :y, :z)"""),
                                           [{"x": barrel.potion_type, "y": barrel.ml_per_barrel*barrel.quantity, "z": "Barrels Purchase"}])
            connection.execute(sqlalchemy.text("""INSERT INTO gold_ledger (change, description) 
                                           VALUES (:x, :y)"""),
                                           [{"x":  -(barrel.quantity*barrel.price), "y": "Barrels Purchased"}])

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    order = []
    # Sort the list by age in descending order
    sorted_wholesale_catalog = sorted(wholesale_catalog, key=lambda barrel: barrel.ml_per_barrel, reverse=True)
    sorted_wholesale_catalog = sorted(sorted_wholesale_catalog, key=lambda barrel: barrel.potion_type, reverse=True)

    
    print(sorted_wholesale_catalog)
    with db.engine.begin() as connection:
        # red_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS red_ml
        #                                              FROM ml_ledger
        #                                             WHERE potion_type = :x"""),[{"x": [1,0,0,0]}]).scalar_one()
        # green_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS green_ml
        #                                              FROM ml_ledger
        #                                             WHERE potion_type = :x"""),[{"x": [0,1,0,0]}]).scalar_one()
        # blue_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS blue_ml
        #                                              FROM ml_ledger
        #                                             WHERE potion_type = :x"""),[{"x": [0,0,1,0]}]).scalar_one()
        # dark_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS dark_ml
        #                                              FROM ml_ledger
        #                                             WHERE potion_type = :x"""),[{"x": [0,0,0,1]}]).scalar_one()
        num_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS ml_tot
                                                     FROM ml_ledger""")).scalar_one()
        gold = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS gold_tot
                                                     FROM gold_ledger""")).scalar_one()
        gold -= 1000

        ml_cap = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(ml_cap), 0) 
                                                    FROM capacity""")).scalar_one()
        
        for barrel in sorted_wholesale_catalog:
            quant = gold//barrel.price
            quant = min(quant, barrel.quantity)
            if barrel.sku == "LARGE_RED_BARREL" and quant > 0 and num_ml+barrel.ml_per_barrel*quant <= ml_cap:
                order.append({
                "sku": "LARGE_RED_BARREL",
                "quantity": 1,
                })  
                gold -= barrel.price
                num_ml += barrel.ml_per_barrel
            if barrel.sku == "LARGE_GREEN_BARREL" and quant > 0 and num_ml+barrel.ml_per_barrel*quant < ml_cap:
                order.append({
                "sku": "LARGE_GREEN_BARREL",
                "quantity": 1,
                })  
                gold -= barrel.price
                num_ml += barrel.ml_per_barrel
                        
            if barrel.sku == "LARGE_BLUE_BARREL" and quant > 0 and num_ml+barrel.ml_per_barrel*quant < ml_cap:
                order.append({
                "sku": "LARGE_BLUE_BARREL",
                "quantity": 1,
                })  
                gold -= barrel.price
                num_ml += barrel.ml_per_barrel
            if barrel.sku == "LARGE_DARK_BARREL" and quant > 0 and num_ml+barrel.ml_per_barrel*quant < ml_cap:
                order.append({
                "sku": "LARGE_DARK_BARREL",
                "quantity": 1,
                })  
                gold -= barrel.price
                num_ml += barrel.ml_per_barrel
            if barrel.sku == "MEDIUM_RED_BARREL" and quant > 0 and num_ml+barrel.ml_per_barrel*quant < ml_cap:
                order.append({
                "sku": "MEDIUM_RED_BARREL",
                "quantity": quant,
                })  
                gold -= barrel.price*quant
                num_ml += barrel.ml_per_barrel
            if barrel.sku == "MEDIUM_GREEN_BARREL" and quant > 0 and num_ml+barrel.ml_per_barrel*quant < ml_cap:
                order.append({
                "sku": "MEDIUM_GREEN_BARREL",
                "quantity": quant,
                })  
                gold -= barrel.price*quant
                num_ml += barrel.ml_per_barrel
                        
            if barrel.sku == "MEDIUM_BLUE_BARREL" and quant > 0 and num_ml+barrel.ml_per_barrel*quant < ml_cap:
                order.append({
                "sku": "MEDIUM_BLUE_BARREL",
                "quantity": quant,
                })  
                gold -= barrel.price*quant
                num_ml += barrel.ml_per_barrel
            if barrel.sku == "MEDIUM_DARK_BARREL" and quant > 0 and num_ml+barrel.ml_per_barrel*quant < ml_cap:
                order.append({
                "sku": "MEDIUM_DARK_BARREL",
                "quantity": quant,
                })  
                gold -= barrel.price*quant
                num_ml += barrel.ml_per_barrel
            if barrel.sku == "SMALL_RED_BARREL" and quant > 0 and num_ml+barrel.ml_per_barrel*quant < ml_cap:
                print("HELLO")
                order.append({
                "sku": "SMALL_RED_BARREL",
                "quantity": quant,
                })  
                gold -= barrel.price*quant
                num_ml += barrel.ml_per_barrel
            if barrel.sku == "SMALL_GREEN_BARREL" and quant > 0 and num_ml+barrel.ml_per_barrel*quant < ml_cap:
                order.append({
                "sku": "SMALL_GREEN_BARREL",
                "quantity": quant,
                })  
                gold -= barrel.price*quant
                num_ml += barrel.ml_per_barrel
                        
            if barrel.sku == "SMALL_BLUE_BARREL" and quant > 0 and num_ml+barrel.ml_per_barrel*quant < ml_cap:
                order.append({
                "sku": "SMALL_BLUE_BARREL",
                "quantity": quant,
                })  
                gold -= barrel.price*quant
                num_ml += barrel.ml_per_barrel
            if barrel.sku == "SMALL_DARK_BARREL" and quant > 0 and num_ml+barrel.ml_per_barrel*quant < ml_cap:
                order.append({
                "sku": "SMALL_DARK_BARREL",
                "quantity": quant,
                })  
                gold -= barrel.price*quant
                num_ml += barrel.ml_per_barrel
  
    return order
    

    

