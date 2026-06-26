from __future__ import annotations

import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Company, ReconciliationRule, User


DEMO_PASSWORD = "demo123"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def seed_defaults(db: Session) -> None:
    company = db.scalar(select(Company).where(Company.name == "Demo Company"))
    if company is None:
        company = Company(name="Demo Company", tax_code="0000000000")
        db.add(company)
        db.flush()

    if db.scalar(select(ReconciliationRule).limit(1)) is None:
        db.add(ReconciliationRule(company_id=company.id))

    demo_users = [
        ("admin@finrecon.local", "Admin", "admin"),
        ("accountant@finrecon.local", "Accountant", "accountant"),
        ("reviewer@finrecon.local", "Reviewer", "reviewer"),
        ("manager@finrecon.local", "Manager", "manager"),
    ]
    existing = set(db.scalars(select(User.email)).all())
    for email, full_name, role in demo_users:
        if email not in existing:
            db.add(
                User(
                    company_id=company.id,
                    email=email,
                    full_name=full_name,
                    role=role,
                    password_hash=hash_password(DEMO_PASSWORD),
                )
            )
