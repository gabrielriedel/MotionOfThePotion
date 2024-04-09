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
        new_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        new_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

    for barrel in barrels_delivered:
        new_green_ml += barrel.ml_per_barrel*barrel.quantity
        new_gold -= barrel.price*barrel.quantity

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = :x").bindparams(x=new_green_ml))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :x").bindparams(x=new_gold))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    with db.engine.begin() as connection:
        num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

    for barrel in wholesale_catalog:
        if barrel.sku == "SMALL_GREEN_BARREL" and num_green_potions < 10 and barrel.price <= gold:
            return [
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": 1,
        }
    ]
        
    return []
    

    

