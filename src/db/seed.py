from datetime import datetime, timedelta, timezone
import random
from src.db.session import get_db, init_db
from src.db.models import Product, CompetitorUrl, PriceLog, AlertLog


def seed_demo_data(force_reseed: bool = False):
    with get_db() as db:
        if not force_reseed and db.query(Product).count() > 0:
            print("Database already seeded.")
            return

        if force_reseed:
            db.query(AlertLog).delete()
            db.query(PriceLog).delete()
            db.query(CompetitorUrl).delete()
            db.query(Product).delete()
            db.commit()

        demo_products = [
            {
                "name": "Wireless Noise-Canceling Headphones X1",
                "category": "Electronics",
                "our_url": "https://store.example.com/headphones-x1",
                "target_price": 299.99,
                "competitors": [
                    {"name": "Our Store", "url": "https://store.example.com/headphones-x1", "is_our_store": True, "base_price": 299.99},
                    {"name": "TechGiant", "url": "https://techgiant.example.com/item/headphones-x1", "is_our_store": False, "base_price": 319.99},
                    {"name": "ElectroMart", "url": "https://electromart.example.com/prod/headphones-x1", "is_our_store": False, "base_price": 289.99},
                    {"name": "ShopDirect", "url": "https://shopdirect.example.com/p/headphones-x1", "is_our_store": False, "base_price": 305.00},
                ],
            },
            {
                "name": "Smart Fitness Watch Series 5",
                "category": "Wearables",
                "our_url": "https://store.example.com/fitness-watch-5",
                "target_price": 199.99,
                "competitors": [
                    {"name": "Our Store", "url": "https://store.example.com/fitness-watch-5", "is_our_store": True, "base_price": 199.99},
                    {"name": "TechGiant", "url": "https://techgiant.example.com/item/watch-5", "is_our_store": False, "base_price": 189.99},
                    {"name": "GearHub", "url": "https://gearhub.example.com/p/watch-5", "is_our_store": False, "base_price": 209.99},
                ],
            },
            {
                "name": "Ultra-Wide Gaming Monitor 34-inch",
                "category": "Computers",
                "our_url": "https://store.example.com/monitor-34",
                "target_price": 499.99,
                "competitors": [
                    {"name": "Our Store", "url": "https://store.example.com/monitor-34", "is_our_store": True, "base_price": 499.99},
                    {"name": "ElectroMart", "url": "https://electromart.example.com/prod/monitor-34", "is_our_store": False, "base_price": 479.99},
                    {"name": "ShopDirect", "url": "https://shopdirect.example.com/p/monitor-34", "is_our_store": False, "base_price": 529.99},
                ],
            },
            {
                "name": "Bluetooth Portable Speaker Pro",
                "category": "Audio",
                "our_url": "https://store.example.com/speaker-pro",
                "target_price": 149.99,
                "competitors": [
                    {"name": "Our Store", "url": "https://store.example.com/speaker-pro", "is_our_store": True, "base_price": 149.99},
                    {"name": "TechGiant", "url": "https://techgiant.example.com/item/speaker-pro", "is_our_store": False, "base_price": 159.99},
                    {"name": "SoundDepot", "url": "https://sounddepot.example.com/p/speaker-pro", "is_our_store": False, "base_price": 139.99},
                ],
            },
            {
                "name": "4K Mirrorless Digital Camera Kit",
                "category": "Cameras",
                "our_url": "https://store.example.com/camera-4k",
                "target_price": 899.99,
                "competitors": [
                    {"name": "Our Store", "url": "https://store.example.com/camera-4k", "is_our_store": True, "base_price": 899.99},
                    {"name": "PhotoWorld", "url": "https://photoworld.example.com/prod/camera-4k", "is_our_store": False, "base_price": 929.00},
                    {"name": "ElectroMart", "url": "https://electromart.example.com/prod/camera-4k", "is_our_store": False, "base_price": 869.99},
                ],
            },
            {
                "name": "Mechanical RGB Gaming Keyboard",
                "category": "Gaming",
                "our_url": "https://store.example.com/keyboard-rgb",
                "target_price": 129.99,
                "competitors": [
                    {"name": "Our Store", "url": "https://store.example.com/keyboard-rgb", "is_our_store": True, "base_price": 129.99},
                    {"name": "GamersZone", "url": "https://gamerszone.example.com/p/keyboard-rgb", "is_our_store": False, "base_price": 119.99},
                    {"name": "TechGiant", "url": "https://techgiant.example.com/item/keyboard-rgb", "is_our_store": False, "base_price": 134.99},
                ],
            },
            {
                "name": "Smart WiFi Thermostat System",
                "category": "Home Automation",
                "our_url": "https://store.example.com/thermostat-smart",
                "target_price": 249.99,
                "competitors": [
                    {"name": "Our Store", "url": "https://store.example.com/thermostat-smart", "is_our_store": True, "base_price": 249.99},
                    {"name": "HomeTech", "url": "https://hometech.example.com/item/thermostat", "is_our_store": False, "base_price": 239.00},
                    {"name": "ShopDirect", "url": "https://shopdirect.example.com/p/thermostat", "is_our_store": False, "base_price": 259.99},
                ],
            },
            {
                "name": "Ergonomic Mesh Office Chair",
                "category": "Office Equipment",
                "our_url": "https://store.example.com/office-chair-mesh",
                "target_price": 349.99,
                "competitors": [
                    {"name": "Our Store", "url": "https://store.example.com/office-chair-mesh", "is_our_store": True, "base_price": 349.99},
                    {"name": "OfficeWorks", "url": "https://officeworks.example.com/prod/chair-mesh", "is_our_store": False, "base_price": 329.99},
                    {"name": "FurnishPlus", "url": "https://furnishplus.example.com/item/chair-mesh", "is_our_store": False, "base_price": 365.00},
                ],
            },
        ]

        now = datetime.now(timezone.utc)

        for p_data in demo_products:
            product = Product(
                name=p_data["name"],
                category=p_data["category"],
                our_url=p_data["our_url"],
                target_price=p_data["target_price"],
            )
            db.add(product)
            db.flush()

            for comp in p_data["competitors"]:
                comp_url = CompetitorUrl(
                    product_id=product.id,
                    competitor_name=comp["name"],
                    is_our_store=comp["is_our_store"],
                    url=comp["url"],
                    is_active=True,
                    last_status="SUCCESS",
                    last_scraped_at=now,
                )
                db.add(comp_url)
                db.flush()

                base = comp["base_price"]
                current_price = base
                for day in range(14, -1, -1):
                    timestamp = now - timedelta(days=day)
                    change_percent = 0.0
                    if day in (10, 5, 2):
                        change_percent = random.choice([-0.08, -0.05, 0.04, 0.06])
                        current_price = round(base * (1 + change_percent), 2)

                    price_log = PriceLog(
                        product_id=product.id,
                        competitor_url_id=comp_url.id,
                        scraped_title=f"{product.name} - {comp['name']}",
                        raw_price_text=f"${current_price:.2f}",
                        price=current_price,
                        currency="USD",
                        is_available=True,
                        scraped_at=timestamp,
                    )
                    db.add(price_log)

                    if day == 5 and change_percent < -0.05:
                        old_p = round(base, 2)
                        new_p = current_price
                        pct = round(((new_p - old_p) / old_p) * 100, 2)
                        alert = AlertLog(
                            product_id=product.id,
                            competitor_url_id=comp_url.id,
                            old_price=old_p,
                            new_price=new_p,
                            pct_change=pct,
                            alert_type="PRICE_DROP" if pct < 0 else "PRICE_INCREASE",
                            message=f"Price dropped by {abs(pct)}% at {comp['name']} (from ${old_p} to ${new_p})",
                            created_at=timestamp,
                        )
                        db.add(alert)

        print("Demo data successfully seeded!")


if __name__ == "__main__":
    init_db()
    seed_demo_data(force_reseed=True)