from starlette.templating import Jinja2Templates
from datetime import datetime
from app.utils import format_price

templates = Jinja2Templates(directory="app/templates")

# Register filters
templates.env.filters['format_price'] = format_price

def format_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

templates.env.filters['format_datetime'] = format_datetime
