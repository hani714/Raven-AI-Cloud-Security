#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from backend.app.models.plans import Subscriptions
from app.models.enums import AnalysisLevel, ScanDepth


def seed_subscriptions(db: Session):
    """Seed subscription plans"""
    
    # Check if subscriptions already exist
    existing_count = db.query(Subscriptions).count()
    if existing_count > 0:
        print(f"Subscriptions already exist ({existing_count} records). Skipping seed.")
        return
    
    subscriptions = [
        Subscriptions(
            name="Free",
            price="0",
            max_environments=1,
            max_scans_per_month=3,
            scan_depth=ScanDepth.quick,
            analysis_level=AnalysisLevel.triage,
            history_days=7
        ),
        Subscriptions(
            name="Basic",
            price="29",
            max_environments=3,
            max_scans_per_month=50,
            scan_depth=ScanDepth.quick,
            analysis_level=AnalysisLevel.deep,
            history_days=30
        ),
        Subscriptions(
            name="Professional",
            price="99",
            max_environments=10,
            max_scans_per_month=200,
            scan_depth=ScanDepth.deep,
            analysis_level=AnalysisLevel.deep,
            history_days=90
        ),
        Subscriptions(
            name="Enterprise",
            price="299",
            max_environments=50,
            max_scans_per_month=1000,
            scan_depth=ScanDepth.deep,
            analysis_level=AnalysisLevel.exploit,
            history_days=365
        ),
    ]
    
    db.add_all(subscriptions)
    db.commit()
    
    print(f"✓ Seeded {len(subscriptions)} subscription plans")


def main():
    """Main function to run all seed operations"""
    print("Starting database seeding...")
    
    db = SessionLocal()
    try:
        seed_subscriptions(db)
        print("✓ Database seeding completed successfully!")
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
