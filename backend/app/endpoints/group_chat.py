from fastapi import APIRouter, Depends
from dotenv import load_dotenv
from typing import *

from app.auth.dependencies import get_current_user
from app.schemas.schemas import *

import app.globals as globals
from app.db.db import *

load_dotenv()

router = APIRouter(prefix="", tags=["chat"])