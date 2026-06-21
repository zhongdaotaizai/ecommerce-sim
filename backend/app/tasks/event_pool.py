EVENT_POOL = [
    {"name": "Electronics Raw Material Price Surge", "description": "Global electronics raw material prices increased by 10% due to supply chain issues", "category_path": "Electronics", "effect_type": "price_up", "effect_value": 0.10, "probability": 0.7},
    {"name": "Beauty Category Mega Promo", "description": "Major beauty brands launch massive promotional campaigns", "category_path": "Beauty", "effect_type": "promotion", "effect_value": 0.15, "probability": 0.8},
    {"name": "Sports Shoes Demand Surge", "description": "New fitness trend drives demand for sports shoes up by 20%", "category_path": "Sports/Shoes", "effect_type": "demand_up", "effect_value": 0.20, "probability": 0.6},
    {"name": "Seasonal Fashion Change", "description": "New season fashion trends cause 15% price drop in last season clothing", "category_path": "Clothing", "effect_type": "price_down", "effect_value": 0.15, "probability": 0.9},
    {"name": "Food Safety Scare", "description": "Food safety concerns reduce demand for snacks by 12%", "category_path": "Food", "effect_type": "demand_down", "effect_value": 0.12, "probability": 0.4},
    {"name": "Winter Clothing Demand Spike", "description": "Early cold wave drives winter clothing demand up by 25%", "category_path": "Clothing/Outerwear", "effect_type": "demand_up", "effect_value": 0.25, "probability": 0.5},
    {"name": "Home Appliance Subsidy", "description": "Government home appliance subsidy program boosts demand by 15%", "category_path": "Home Appliances", "effect_type": "demand_up", "effect_value": 0.15, "probability": 0.5},
    {"name": "Luxury Tax Increase", "description": "New luxury tax causes 8% price increase on premium goods", "category_path": "Luxury", "effect_type": "price_up", "effect_value": 0.08, "probability": 0.3},
    {"name": "Eco-Friendly Trend", "description": "Eco-friendly products see 18% demand increase", "category_path": "Home", "effect_type": "demand_up", "effect_value": 0.18, "probability": 0.6},
    {"name": "Book Reading Festival", "description": "National reading festival boosts book sales by 20%", "category_path": "Books", "effect_type": "demand_up", "effect_value": 0.20, "probability": 0.5},
    {"name": "Pet Supplies Boom", "description": "Pet ownership surge drives pet supplies demand up by 22%", "category_path": "Pet Supplies", "effect_type": "demand_up", "effect_value": 0.22, "probability": 0.4},
    {"name": "Electronic Component Shortage", "description": "Global chip shortage raises electronics prices by 12%", "category_path": "Electronics", "effect_type": "price_up", "effect_value": 0.12, "probability": 0.6},
    {"name": "Fitness Equipment Demand", "description": "New Year resolution fitness trend boosts equipment sales by 30%", "category_path": "Sports", "effect_type": "demand_up", "effect_value": 0.30, "probability": 0.5},
    {"name": "Organic Food Movement", "description": "Organic food demand surges 25% following health report", "category_path": "Food/Organic", "effect_type": "demand_up", "effect_value": 0.25, "probability": 0.4},
    {"name": "Travel Season Boost", "description": "Peak travel season drives luggage and travel accessory demand", "category_path": "Travel", "effect_type": "demand_up", "effect_value": 0.20, "probability": 0.7},
    {"name": "Tech Product Launch Season", "description": "New tech product launches cause 10% price drop on older models", "category_path": "Electronics", "effect_type": "price_down", "effect_value": 0.10, "probability": 0.6},
    {"name": "Rainy Season Gear Demand", "description": "Rainy season increases umbrella and raincoat demand by 35%", "category_path": "Clothing/Accessories", "effect_type": "demand_up", "effect_value": 0.35, "probability": 0.3},
    {"name": "Toy Safety Recall", "description": "Toy safety concerns reduce toy category demand by 15%", "category_path": "Toys", "effect_type": "demand_down", "effect_value": 0.15, "probability": 0.3},
    {"name": "Mother's Day Gift Season", "description": "Mother's Day drives gift and jewelry category demand up 20%", "category_path": "Jewelry", "effect_type": "demand_up", "effect_value": 0.20, "probability": 0.5},
    {"name": "Back-to-School Season", "description": "Back-to-school drives stationery and bag demand up 28%", "category_path": "Stationery", "effect_type": "demand_up", "effect_value": 0.28, "probability": 0.7},
]
DEFAULT_EVENTS = EVENT_POOL.copy()
def get_event_pool():
    return DEFAULT_EVENTS
def sample_events(min_count: int = 1, max_count: int = 3):
    import random
    pool = get_event_pool()
    count = random.randint(min_count, max_count)
    weights = [e["probability"] for e in pool]
    sampled = random.choices(pool, weights=weights, k=min(count, len(pool)))
    return sampled
def apply_event_to_price(price: float, event: dict) -> float:
    if event["effect_type"] == "price_up":
        return price * (1 + event["effect_value"])
    elif event["effect_type"] == "price_down":
        return price * (1 - event["effect_value"])
    return price
def get_event_category_filter(event: dict) -> str:
    return event.get("category_path", "")
def get_event_demand_modifier(event: dict) -> float:
    if event["effect_type"] == "demand_up":
        return 1.0 + event["effect_value"]
    elif event["effect_type"] == "demand_down":
        return 1.0 - event["effect_value"]
    return 1.0
def get_event_price_modifier(event: dict) -> float:
    if event["effect_type"] == "price_up":
        return 1.0 + event["effect_value"]
    elif event["effect_type"] == "price_down":
        return 1.0 - event["effect_value"]
    elif event["effect_type"] == "promotion":
        return max(0.7, 1.0 - event["effect_value"])
    return 1.0
