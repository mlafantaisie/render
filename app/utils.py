def format_price(copper: int) -> str:
    gold = copper // 10000
    silver = (copper % 10000) // 100
    copper_remain = copper % 100
    return f"{gold}g {silver}s {copper_remain}c"
