from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    with db.engine.begin() as connection:
        
        connection.execute(sqlalchemy.text("""DELETE FROM ml_ledger 
                                           WHERE id != (SELECT MIN(id) FROM ml_ledger)"""))
        connection.execute(sqlalchemy.text("""DELETE FROM gold_ledger 
                                           WHERE id != (SELECT MIN(id) FROM gold_ledger)"""))
        connection.execute(sqlalchemy.text("""DELETE FROM potion_ledger 
                                           WHERE id != (SELECT MIN(id) FROM potion_ledger)"""))
        
        
        
    return "OK"

