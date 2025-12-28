import strawberry
from sqlalchemy import select
from sqlalchemy.orm import selectinload

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
    async def abstract_products(
        self,
        info: strawberry.Info,
    ) -> list[AbstractProductType]:
        session = info.context["session"]
        result = await session.execute(select(AbstractProduct))
        return list(result.scalars().all())

    @strawberry.field(description="Get a specific abstract product by ID.")
    async def abstract_product(
        self,
        info: strawberry.Info,
        id: int,
    ) -> AbstractProductType | None:
        session = info.context["session"]
        result = await session.execute(
            select(AbstractProduct).where(AbstractProduct.id == id)
        )
        return result.scalar_one_or_none()

    @strawberry.field(description="Get a list of all producers.")
    async def producers(self, info: strawberry.Info) -> list[ProducerType]:
        session = info.context["session"]
        result = await session.execute(select(Producer))
        return list(result.scalars().all())

    @strawberry.field(description="Get a specific producer by ID.")
    async def producer(self, info: strawberry.Info, id: int) -> ProducerType | None:
        session = info.context["session"]
        result = await session.execute(select(Producer).where(Producer.id == id))
        return result.scalar_one_or_none()

    @strawberry.field(description="Get a specific producer by code.")
    async def producer_by_code(
        self, info: strawberry.Info, code: str
    ) -> ProducerType | None:
        session = info.context["session"]
        result = await session.execute(select(Producer).where(Producer.code == code))
        return result.scalar_one_or_none()

    @strawberry.field(
        description="Get a list of all products. Optional: filter by producer code."
    )
    async def products(
        self, info: strawberry.Info, producer_code: str | None = None
    ) -> list[ProductType]:
        session = info.context["session"]
        query = select(Product).options(
            selectinload(Product.producer), selectinload(Product.abstract_product)
        )

        if producer_code:
            query = query.join(Product.producer).where(Producer.code == producer_code)
        result = await session.execute(query)
        return list(result.scalars().all())

    @strawberry.field(description="Get a specific product by ID.")
    async def product(self, info: strawberry.Info, id: int) -> ProductType | None:
        session = info.context["session"]
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
    async def production_chains(
        self, info: strawberry.Info
    ) -> list[ProductionChainType]:
        session = info.context["session"]
        query = select(ProductionChain).options(
            selectinload(ProductionChain.input_product),
            selectinload(ProductionChain.output_product),
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    @strawberry.field(description="Get a specific production chain by ID.")
    async def production_chain(
        self, info: strawberry.Info, id: int
    ) -> ProductionChainType | None:
        session = info.context["session"]
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
    async def chains_using_product(
        self, info: strawberry.Info, product_id: int
    ) -> list[ProductionChainType]:
        session = info.context["session"]
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
        self, info: strawberry.Info, product_id: int
    ) -> list[ProductionChainType]:
        session = info.context["session"]
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
    async def plans(self, info: strawberry.Info) -> list[ProductionPlanType]:
        session = info.context["session"]
        query = select(ProductionPlan).options(
            selectinload(ProductionPlan.plan_values),
            selectinload(ProductionPlan.sub_plans),
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    @strawberry.field(description="Get a specific production plan by ID.")
    async def plan(self, info: strawberry.Info, id: int) -> ProductionPlanType | None:
        session = info.context["session"]
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
    async def plan_values(self, info: strawberry.Info) -> list[PlanValueType]:
        session = info.context["session"]
        query = select(PlanValue).options(
            selectinload(PlanValue.product), selectinload(PlanValue.plan)
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    @strawberry.field(description="Get a specific plan value by ID.")
    async def plan_value(self, info: strawberry.Info, id: int) -> PlanValueType | None:
        session = info.context["session"]
        query = (
            select(PlanValue)
            .options(selectinload(PlanValue.product), selectinload(PlanValue.plan))
            .where(PlanValue.id == id)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @strawberry.field(description="Get all plan values for a specific production plan.")
    async def plan_values_for_plan(
        self, info: strawberry.Info, plan_id: int
    ) -> list[PlanValueType]:
        session = info.context["session"]
        query = (
            select(PlanValue)
            .where(PlanValue.plan_id == plan_id)
            .options(selectinload(PlanValue.product), selectinload(PlanValue.plan))
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    @strawberry.field(description="Get all plan values for a specific product.")
    async def plan_values_for_product(
        self, info: strawberry.Info, product_id: int
    ) -> list[PlanValueType]:
        session = info.context["session"]
        query = (
            select(PlanValue)
            .where(PlanValue.product_id == product_id)
            .options(selectinload(PlanValue.product), selectinload(PlanValue.plan))
        )
        result = await session.execute(query)
        return list(result.scalars().all())


schema = strawberry.Schema(query=Query)
