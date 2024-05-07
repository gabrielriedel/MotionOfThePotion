from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        num_potions = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS potion_tot
                                                     FROM potion_ledger""")).scalar_one()
        gold = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS gold_tot
                                                     FROM gold_ledger""")).scalar_one()
        num_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS ml_tot
                                                     FROM ml_ledger""")).scalar_one()

    return {"number_of_potions": num_potions, "ml_in_barrels": num_ml, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    with db.engine.begin() as connection:
        num_potions = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS potion_tot
                                                     FROM potion_ledger""")).scalar_one()
        gold = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS gold_tot
                                                     FROM gold_ledger""")).scalar_one()
        num_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS ml_tot
                                                     FROM ml_ledger""")).scalar_one()
        
        ml_cap_quant = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(ml_cap), 0) 
                                                    FROM capacity""")).scalar_one()
        pot_cap_quant = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(potion_cap), 0) 
                                                     FROM capacity""")).scalar_one()
        
        pot_cap = 0
        ml_cap = 0
        #num_ml >= ml_cap_quant//2 and 

        if gold >= 1500:
            gold -= 1000
            pot_cap = 1
        
        if gold >= 1500:
            ml_cap = 1
        
        return {
                "potion_capacity": pot_cap,
                "ml_capacity": ml_cap
                    }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""INSERT INTO capacity (ml_cap, potion_cap) 
                                           VALUES (:x, :y)"""),
                                           [{"x": 10000*capacity_purchase.ml_capacity, "y": 50*capacity_purchase.potion_capacity}])
        connection.execute(sqlalchemy.text("""INSERT INTO gold_ledger (change, description) 
                                           VALUES (:x, :y)"""),
                                           [{"x":  -((1000*capacity_purchase.ml_capacity)+(1000*capacity_purchase.potion_capacity)), "y": "Capacity Purchased"}])

    return "OK"
