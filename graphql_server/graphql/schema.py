import strawberry
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from graphql_server.database import get_db
from graphql_server.models import (
    Product,
    Producer,
    ProductionPlan,
)
from graphql_server.graphql.types import (
    PlanValueType,
    ProductType,
    ProductionPlanType,
)


@strawberry.type
class Query:
    @strawberry.field(
        description="Get a list of all products. Optional: filter by producer code."
    )
    async def products(self, producer_code: str | None = None) -> list[ProductType]:
        query = select(Product).options(
            selectinload(Product.producer), selectinload(Product.abstract_product)
        )

        if producer_code:
            # Example of joining to filter, useful for LLM logic testing
            query = query.join(Product.producer).where(Producer.code == producer_code)
        # Logic to fetch products
        async for session in get_db():
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
                        PlanValueType.product
                    )
                )
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    # TODO: Add resolvers for 'producers', 'chains', and complex filters
    # (e.g., finding chains where specific input product is used)
    # This will allow you to test if the LLM can construct deep nested queries.


schema = strawberry.Schema(query=Query)
