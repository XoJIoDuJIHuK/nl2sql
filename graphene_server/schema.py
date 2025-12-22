import graphene
from graphene import ObjectType, String, Int, Float, List, Field, Boolean
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import models

# --- Object Types ---


class AbstractProductType(ObjectType):
    id = Int()
    name = String()


class ProducerType(ObjectType):
    id = Int()
    code = String()


class ProductType(ObjectType):
    id = Int()
    code = String()
    abstract_product = Field(AbstractProductType)
    producer = Field(ProducerType)

    # Custom resolver to handle async relationship loading if needed
    # (Simplified for context, assumes eager loading or simple scalar access)


class ProductionChainType(ObjectType):
    id = Int()
    amount = Float()
    input_product = Field(ProductType)
    output_product = Field(ProductType)


class PlanValueType(ObjectType):
    id = Int()
    value = Float()
    product = Field(ProductType)


class ProductionPlanType(ObjectType):
    id = Int()
    is_external = Boolean()
    # To avoid circular dependency issues in Graphene, we can use a string or lambda
    master_plan = Field(lambda: ProductionPlanType)
    sub_plans = List(lambda: ProductionPlanType)
    values = List(PlanValueType)

    async def resolve_values(root, info):
        # Resolver logic to fetch values asynchronously if not eagerly loaded
        return root.values


# --- Query Root ---


class Query(ObjectType):
    # Field definitions
    abstract_products = List(AbstractProductType)
    producers = List(ProducerType)
    products = List(ProductType, producer_code=String(required=False))
    production_chains = List(ProductionChainType)
    production_plans = List(ProductionPlanType, is_master=Boolean(required=False))
    plan_values = List(PlanValueType, plan_id=Int(required=True))

    # --- Resolvers ---

    async def resolve_abstract_products(root, info):
        session = info.context["session"]
        result = await session.execute(select(models.AbstractProduct))
        return result.scalars().all()

    async def resolve_producers(root, info):
        session = info.context["session"]
        result = await session.execute(select(models.Producer))
        return result.scalars().all()

    async def resolve_products(root, info, producer_code=None):
        session = info.context["session"]
        query = select(models.Product).options(
            selectinload(models.Product.abstract_product),
            selectinload(models.Product.producer),
        )

        if producer_code:
            query = query.join(models.Producer).where(
                models.Producer.code == producer_code
            )

        result = await session.execute(query)
        return result.scalars().all()

    async def resolve_production_chains(root, info):
        session = info.context["session"]
        # Eager load relationships to avoid N+1 in async
        query = select(models.ProductionChain).options(
            selectinload(models.ProductionChain.input_product).options(
                selectinload(models.Product.abstract_product)
            ),
            selectinload(models.ProductionChain.output_product),
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def resolve_production_plans(root, info, is_master=None):
        session = info.context["session"]
        query = select(models.ProductionPlan).options(
            selectinload(models.ProductionPlan.values).selectinload(
                models.PlanValue.product
            )
        )

        if is_master is not None:
            if is_master:
                query = query.where(models.ProductionPlan.master_plan_id == None)
            else:
                query = query.where(models.ProductionPlan.master_plan_id != None)

        result = await session.execute(query)
        return result.scalars().all()

    async def resolve_plan_values(root, info, plan_id):
        session = info.context["session"]
        query = (
            select(models.PlanValue)
            .where(models.PlanValue.plan_id == plan_id)
            .options(selectinload(models.PlanValue.product))
        )
        result = await session.execute(query)
        return result.scalars().all()


# # --- Mutation Root ---
# class Mutation(ObjectType):
#     # TODO: Implement mutations for creating Products, Chains, and Plans.
#     # Leaving empty for now as requested to save context space.
#     pass


schema = graphene.Schema(query=Query)
