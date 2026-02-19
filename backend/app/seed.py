"""Seed script for demo location data and users."""
import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.location import City, Community, Country
from app.models.payment import Wallet
from app.models.user import User
from app.core.security import hash_password

SEED_DATA = {
    ("United Arab Emirates", "AE", "AED"): {
        "Dubai": [
            "Jumeirah Park", "Dubai Marina", "Jumeirah Village Circle", "Jumeirah Village Triangle",
            "Arabian Ranches", "Arabian Ranches 2", "Arabian Ranches 3",
            "Dubai Hills Estate", "Downtown Dubai", "Business Bay",
            "Palm Jumeirah", "Jumeirah Beach Residence", "DIFC",
            "City Walk", "Al Barsha", "Motor City",
            "Dubai Sports City", "International City", "Discovery Gardens",
            "Al Furjan", "Mudon", "Damac Hills", "Damac Hills 2",
            "Town Square", "Remraam", "The Springs",
            "The Meadows", "The Lakes", "Emirates Hills",
            "Jumeirah Islands", "Jumeirah Golf Estates", "Dubai South",
            "Al Quoz", "Mirdif", "Al Warqa", "Silicon Oasis",
            "Academic City", "Dubai Creek Harbour", "Sobha Hartland",
            "MBR City", "Al Nahda", "Deira", "Bur Dubai",
            "Karama", "Oud Metha", "Umm Suqeim",
            "Jumeirah", "Satwa", "Barsha Heights", "Tilal Al Ghaf",
        ],
        "Abu Dhabi": [
            "Yas Island", "Saadiyat Island", "Al Reem Island", "Al Raha Beach",
            "Khalifa City", "Mohammed Bin Zayed City", "Al Reef",
            "Corniche Area", "Tourist Club Area", "Al Mushrif",
        ],
        "Sharjah": ["Al Nahda", "Al Majaz", "Al Khan", "University City"],
    },
    ("United Kingdom", "GB", "GBP"): {
        "London": [
            "Canary Wharf", "Kensington", "Chelsea", "Camden",
            "Shoreditch", "Hackney", "Brixton", "Greenwich",
            "Islington", "Stratford",
        ],
        "Manchester": ["City Centre", "Salford Quays", "Didsbury", "Ancoats"],
        "Birmingham": ["City Centre", "Edgbaston", "Jewellery Quarter"],
    },
    ("United States", "US", "USD"): {
        "New York": [
            "Manhattan", "Brooklyn", "Queens", "Bronx",
            "Upper East Side", "Williamsburg", "Harlem",
        ],
        "Los Angeles": ["Santa Monica", "Hollywood", "Downtown LA", "Venice"],
        "Miami": ["Brickell", "Wynwood", "South Beach", "Coconut Grove"],
    },
}


async def seed_locations(db: AsyncSession) -> None:
    result = await db.execute(select(Country).limit(1))
    if result.scalar_one_or_none():
        print("Locations already seeded, skipping.")
        return

    total_communities = 0
    for (country_name, code, currency), cities_data in SEED_DATA.items():
        country = Country(id=uuid.uuid4(), name=country_name, code=code, currency_code=currency)
        db.add(country)
        await db.flush()

        for city_name, communities in cities_data.items():
            city = City(id=uuid.uuid4(), country_id=country.id, name=city_name)
            db.add(city)
            await db.flush()

            city_slug = city_name.lower().replace(" ", "-")
            for comm_name in communities:
                slug = f"{city_slug}-{comm_name.lower().replace(' ', '-').replace(chr(39), '')}"
                community = Community(id=uuid.uuid4(), city_id=city.id, name=comm_name, slug=slug)
                db.add(community)
                total_communities += 1

    await db.flush()
    print(f"Seeded {total_communities} communities across {len(SEED_DATA)} countries.")


async def seed_demo_users(db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.email == "admin@tenanttruth.com").limit(1))
    if result.scalar_one_or_none():
        print("Demo users already seeded, skipping.")
        return

    pw = hash_password("Password123!")

    admin = User(
        id=uuid.uuid4(), email="admin@tenanttruth.com", password_hash=pw,
        first_name="Admin", last_name="User", role="admin",
        auth_provider="email", is_email_verified=True, is_active=True,
    )
    tenant = User(
        id=uuid.uuid4(), email="tenant@demo.com", password_hash=pw,
        first_name="Demo", last_name="Tenant", role="tenant",
        auth_provider="email", is_email_verified=True, is_active=True,
        is_contactable=True,
    )
    landlord = User(
        id=uuid.uuid4(), email="landlord@demo.com", password_hash=pw,
        first_name="Demo", last_name="Landlord", role="landlord",
        auth_provider="email", is_email_verified=True, is_active=True,
    )

    db.add_all([admin, tenant, landlord])
    await db.flush()

    for user, credits in [(admin, 0), (tenant, 100), (landlord, 50)]:
        wallet = Wallet(user_id=user.id, balance_credits=credits)
        db.add(wallet)

    await db.flush()
    print("Seeded demo users (admin/tenant/landlord) with wallets.")


async def main():
    async with async_session_factory() as db:
        await seed_locations(db)
        await seed_demo_users(db)
        await db.commit()
    print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(main())
