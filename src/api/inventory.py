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
        # num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
        # num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
        # num_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()
        # num_ml = num_red_ml + num_green_ml + num_blue_ml

        # result = connection.execute(sqlalchemy.text("SELECT inventory FROM potions"))
        # num_potions = 0
        # for row in result:
        #     num_potions += row.inventory

        # gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar_one()

    return {"number_of_potions": num_potions, "ml_in_barrels": num_ml, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
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

    return "OK"
