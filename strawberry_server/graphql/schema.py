import strawberry
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import get_db
from database.models import (
    AbstractProduct,
    PlanValue,
    Product,
    Producer,
    ProductionChain,
    ProductionPlan,
)
from strawberry_server.graphql.types import (
    AbstractProductType,
    PlanValueType,
    ProductType,
    ProductionChainType,
    ProductionPlanType,
    ProducerType,
)


@strawberry.type
class Query:
    @strawberry.field(description="Get a list of all abstract products.")
    async def abstract_products(self) -> list[AbstractProductType]:
        async for session in get_db():
            result = await session.execute(select(AbstractProduct))
        return list(result.scalars().all())

    @strawberry.field(description="Get a specific abstract product by ID.")
    async def abstract_product(self, id: int) -> AbstractProductType | None:
        async for session in get_db():
            result = await session.execute(
                select(AbstractProduct).where(AbstractProduct.id == id)
            )
        return result.scalar_one_or_none()

    @strawberry.field(description="Get a list of all producers.")
    async def producers(self) -> list[ProducerType]:
        async for session in get_db():
            result = await session.execute(select(Producer))
        return list(result.scalars().all())

    @strawberry.field(description="Get a specific producer by ID.")
    async def producer(self, id: int) -> ProducerType | None:
        async for session in get_db():
            result = await session.execute(select(Producer).where(Producer.id == id))
        return result.scalar_one_or_none()

    @strawberry.field(description="Get a specific producer by code.")
    async def producer_by_code(self, code: str) -> ProducerType | None:
        async for session in get_db():
            result = await session.execute(
                select(Producer).where(Producer.code == code)
            )
        return result.scalar_one_or_none()

    @strawberry.field(
        description="Get a list of all products. Optional: filter by producer code."
    )
    async def products(self, producer_code: str | None = None) -> list[ProductType]:
        query = select(Product).options(
            selectinload(Product.producer), selectinload(Product.abstract_product)
        )

        if producer_code:
            query = query.join(Product.producer).where(Producer.code == producer_code)
        async for session in get_db():
            result = await session.execute(query)
        return list(result.scalars().all())

    @strawberry.field(description="Get a specific product by ID.")
    async def product(self, id: int) -> ProductType | None:
        async for session in get_db():
            query = (
                select(Product)
                .options(
                    selectinload(Product.producer),
                    selectinload(Product.abstract_product),
                )
                .where(Product.id == id)
            )
            result = await session.execute(query)
        return result.scalar_one_or_none()

    @strawberry.field(description="Get a list of all production chains.")
    async def production_chains(self) -> list[ProductionChainType]:
        async for session in get_db():
            query = select(ProductionChain).options(
                selectinload(ProductionChain.input_product),
                selectinload(ProductionChain.output_product),
            )
            result = await session.execute(query)
        return list(result.scalars().all())

    @strawberry.field(description="Get a specific production chain by ID.")
    async def production_chain(self, id: int) -> ProductionChainType | None:
        async for session in get_db():
            query = (
                select(ProductionChain)
                .options(
                    selectinload(ProductionChain.input_product),
                    selectinload(ProductionChain.output_product),
                )
                .where(ProductionChain.id == id)
            )
            result = await session.execute(query)
        return result.scalar_one_or_none()

    @strawberry.field(
        description="Get production chains where a specific product is used as input."
    )
    async def chains_using_product(self, product_id: int) -> list[ProductionChainType]:
        async for session in get_db():
            query = (
                select(ProductionChain)
                .where(ProductionChain.input_product_id == product_id)
                .options(
                    selectinload(ProductionChain.input_product),
                    selectinload(ProductionChain.output_product),
                )
            )
            result = await session.execute(query)
        return list(result.scalars().all())

    @strawberry.field(
        description="Get production chains where a specific product is produced."
    )
    async def chains_producing_product(
        self, product_id: int
    ) -> list[ProductionChainType]:
        async for session in get_db():
            query = (
                select(ProductionChain)
                .where(ProductionChain.output_product_id == product_id)
                .options(
                    selectinload(ProductionChain.input_product),
                    selectinload(ProductionChain.output_product),
                )
            )
            result = await session.execute(query)
        return list(result.scalars().all())

    @strawberry.field(description="Get a list of all production plans.")
    async def plans(self) -> list[ProductionPlanType]:
        async for session in get_db():
            query = select(ProductionPlan).options(
                selectinload(ProductionPlan.plan_values),
                selectinload(ProductionPlan.sub_plans),
            )
            result = await session.execute(query)
        return list(result.scalars().all())

    @strawberry.field(description="Get a specific production plan by ID.")
    async def plan(self, id: int) -> ProductionPlanType | None:
        async for session in get_db():
            query = (
                select(ProductionPlan)
                .where(ProductionPlan.id == id)
                .options(
                    selectinload(ProductionPlan.plan_values).selectinload(
                        PlanValue.product
                    ),
                    selectinload(ProductionPlan.sub_plans),
                )
            )
            result = await session.execute(query)
        return result.scalar_one_or_none()

    @strawberry.field(description="Get all plan values.")
    async def plan_values(self) -> list[PlanValueType]:
        async for session in get_db():
            query = select(PlanValue).options(
                selectinload(PlanValue.product), selectinload(PlanValue.plan)
            )
            result = await session.execute(query)
        return list(result.scalars().all())

    @strawberry.field(description="Get a specific plan value by ID.")
    async def plan_value(self, id: int) -> PlanValueType | None:
        async for session in get_db():
            query = (
                select(PlanValue)
                .options(selectinload(PlanValue.product), selectinload(PlanValue.plan))
                .where(PlanValue.id == id)
            )
            result = await session.execute(query)
        return result.scalar_one_or_none()

    @strawberry.field(description="Get all plan values for a specific production plan.")
    async def plan_values_for_plan(self, plan_id: int) -> list[PlanValueType]:
        async for session in get_db():
            query = (
                select(PlanValue)
                .where(PlanValue.plan_id == plan_id)
                .options(selectinload(PlanValue.product), selectinload(PlanValue.plan))
            )
            result = await session.execute(query)
        return list(result.scalars().all())

    @strawberry.field(description="Get all plan values for a specific product.")
    async def plan_values_for_product(self, product_id: int) -> list[PlanValueType]:
        async for session in get_db():
            query = (
                select(PlanValue)
                .where(PlanValue.product_id == product_id)
                .options(selectinload(PlanValue.product), selectinload(PlanValue.plan))
            )
            result = await session.execute(query)
        return list(result.scalars().all())


schema = strawberry.Schema(query=Query)
