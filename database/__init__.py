"""Unified database package for production management system."""

# Core database components
from .core import Base, async_session_maker, create_all_tables, drop_all_tables, engine

# Configuration
from .config import settings

# Dependencies
from .dependencies import get_db

# Models
from .models import (
    AbstractProduct,
    PlanValue,
    Producer,
    Product,
    ProductionChain,
    ProductionPlan,
)

__all__ = [
    # Core
    "Base",
    "engine",
    "async_session_maker",
    "create_all_tables",
    "drop_all_tables",
    # Configuration
    "settings",
    # Dependencies
    "get_db",
    # Models
    "AbstractProduct",
    "Producer",
    "Product",
    "ProductionChain",
    "ProductionPlan",
    "PlanValue",
]