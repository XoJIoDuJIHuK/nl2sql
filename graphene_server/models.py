from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Numeric,
    Boolean,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from graphene_server.database import Base


class AbstractProduct(Base):
    __tablename__ = "abstract_products"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # Relationships
    concrete_products = relationship("Product", back_populates="abstract_product")


class Producer(Base):
    __tablename__ = "producers"

    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False)

    products = relationship("Product", back_populates="producer")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    production_id = Column(Integer, ForeignKey("abstract_products.id"), nullable=False)
    producer_id = Column(Integer, ForeignKey("producers.id"), nullable=False)
    code = Column(String(20), nullable=False)

    # Relationships
    abstract_product = relationship(
        "AbstractProduct", back_populates="concrete_products"
    )
    producer = relationship("Producer", back_populates="products")

    # Chains where this product is the input
    inputs_for = relationship(
        "ProductionChain",
        foreign_keys="[ProductionChain.input_product_id]",
        back_populates="input_product",
    )
    # Chains where this product is the output
    produced_by = relationship(
        "ProductionChain",
        foreign_keys="[ProductionChain.output_product_id]",
        back_populates="output_product",
    )

    plan_values = relationship("PlanValue", back_populates="product")


class ProductionChain(Base):
    __tablename__ = "production_chains"

    id = Column(Integer, primary_key=True)
    input_product_id = Column(Integer, ForeignKey("products.id"))
    output_product_id = Column(Integer, ForeignKey("products.id"))
    amount = Column(Numeric(20, 6), nullable=False)

    input_product = relationship(
        "Product", foreign_keys=[input_product_id], back_populates="inputs_for"
    )
    output_product = relationship(
        "Product", foreign_keys=[output_product_id], back_populates="produced_by"
    )


class ProductionPlan(Base):
    __tablename__ = "production_plans"

    id = Column(Integer, primary_key=True)
    master_plan_id = Column(Integer, ForeignKey("production_plans.id"), nullable=True)
    is_external = Column(Boolean, nullable=False, default=False)

    # Self-referential relationship for sub-plans
    sub_plans = relationship("ProductionPlan", backref="master_plan", remote_side=[id])
    values = relationship("PlanValue", back_populates="plan")

    __table_args__ = (
        CheckConstraint(
            "(is_external AND master_plan_id IS NULL) OR (NOT is_external AND master_plan_id IS NOT NULL)",
            name="check_for_master_plan_values",
        ),
    )


class PlanValue(Base):
    __tablename__ = "plan_values"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    plan_id = Column(Integer, ForeignKey("production_plans.id"))
    value = Column(Numeric(20, 6), nullable=False)

    product = relationship("Product", back_populates="plan_values")
    plan = relationship("ProductionPlan", back_populates="values")
