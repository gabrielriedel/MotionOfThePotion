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
        results = connection.execute(sqlalchemy.text("""SELECT 
                                                     num_red_ml, 
                                                     num_green_ml, 
                                                     num_blue_ml, 
                                                     num_dark_ml, 
                                                     gold 
                                                     FROM global_inventory""")).fetchone()
    
    inventory_data = list(results)

    for barrel in barrels_delivered:
        if barrel.potion_type == [1,0,0,0]:
            inventory_data[0] += barrel.ml_per_barrel*barrel.quantity
            inventory_data[4] -= barrel.price*barrel.quantity
        elif barrel.potion_type == [0,1,0,0]:
            inventory_data[1] += barrel.ml_per_barrel*barrel.quantity
            inventory_data[4] -= barrel.price*barrel.quantity
        elif barrel.potion_type == [0,0,1,0]:
            inventory_data[2] += barrel.ml_per_barrel*barrel.quantity
            inventory_data[4] -= barrel.price*barrel.quantity
        elif barrel.potion_type == [0,0,0,1]:
            inventory_data[3] += barrel.ml_per_barrel*barrel.quantity
            inventory_data[4] -= barrel.price*barrel.quantity
        else:
            raise Exception("Invalid Potion Type")
    
    # .text(""),[{"red_ml": red_ml, "green_ml": }]

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :x"),[{"x": inventory_data[0]}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = :x"),[{"x": inventory_data[1]}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = :x"),[{"x": inventory_data[2]}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_dark_ml = :x"),[{"x": inventory_data[3]}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :x"),[{"x": inventory_data[4]}])

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    order = []
    print(wholesale_catalog)
    with db.engine.begin() as connection:
        results = connection.execute(sqlalchemy.text("""SELECT 
                                                     num_red_ml, 
                                                     num_green_ml, 
                                                     num_blue_ml, 
                                                     num_dark_ml, 
                                                     gold 
                                                     FROM global_inventory""")).fetchone()
    inventory_data = list(results)
    for barrel in wholesale_catalog:
        if barrel.sku == "MEDIUM_RED_BARREL" and inventory_data[0] < 1000 and inventory_data[1] < 500 and inventory_data[2] < 500 and inventory_data[3] < 500 and barrel.price <= inventory_data[4]:
            order.append({
            "sku": "MEDIUM_RED_BARREL",
            "quantity": 1,
            })  
            inventory_data[4] -= barrel.price
        if barrel.sku == "MEDIUM_GREEN_BARREL" and inventory_data[0] > inventory_data[1] and barrel.price <= inventory_data[4]:
            order.append({
            "sku": "MEDIUM_GREEN_BARREL",
            "quantity": 1,
            })  
            inventory_data[4] -= barrel.price
                    
        if barrel.sku == "MEDIUM_BLUE_BARREL" and inventory_data[0] > inventory_data[2] and inventory_data[1] > inventory_data[2] and barrel.price <= inventory_data[4]:
            order.append({
            "sku": "MEDIUM_BLUE_BARREL",
            "quantity": 1,
            })  
            inventory_data[4] -= barrel.price
        if barrel.sku == "MEDIUM_DARK_BARREL" and barrel.price <= inventory_data[4]:
            order.append({
            "sku": "MEDIUM_DARK_BARREL",
            "quantity": 1,
            })  
            inventory_data[4] -= barrel.price
        if barrel.sku == "SMALL_RED_BARREL" and inventory_data[0] < 1000 and inventory_data[1] < 500 and inventory_data[2] < 500 and inventory_data[3] < 500 and barrel.price <= inventory_data[4]:
            order.append({
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
            })  
            inventory_data[4] -= barrel.price
        if barrel.sku == "SMALL_GREEN_BARREL" and inventory_data[0] > inventory_data[1] and barrel.price <= inventory_data[4]:
            order.append({
            "sku": "SMALL_GREEN_BARREL",
            "quantity": 1,
            })  
            inventory_data[4] -= barrel.price
                    
        if barrel.sku == "SMALL_BLUE_BARREL" and inventory_data[0] > inventory_data[2] and inventory_data[1] > inventory_data[2] and barrel.price <= inventory_data[4]:
            order.append({
            "sku": "SMALL_BLUE_BARREL",
            "quantity": 1,
            })  
            inventory_data[4] -= barrel.price
        if barrel.sku == "SMALL_DARK_BARREL" and barrel.price <= inventory_data[4]:
            order.append({
            "sku": "SMALL_DARK_BARREL",
            "quantity": 1,
            })  
            inventory_data[4] -= barrel.price
        
        
    return order
    

    

