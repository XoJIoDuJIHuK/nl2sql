import strawberry
from typing import List, Optional
from strawberry.types import Info


# Use 'lazy' types to handle circular dependencies nicely
@strawberry.type(
    description="Abstract products that define the general category of items."
)
class AbstractProductType:
    id: int
    name: str

    # TODO: Implement concrete_products resolver if needed for reverse lookups


@strawberry.type(description="Manufacturing entities that produce products.")
class ProducerType:
    id: int
    code: str


@strawberry.type(description="A specific concrete product implementation.")
class ProductType:
    id: int

    @strawberry.field(description="The generic category this product belongs to.")
    async def abstract_product(self, info: Info) -> AbstractProductType:
        # DataLoaders should be used here in production for performance
        return self.abstract_product

    @strawberry.field(description="The manufacturer of this product.")
    async def producer(self, info: Info) -> ProducerType:
        return self.producer


@strawberry.type(description="Defines the input/output relationship between products.")
class ProductionChainType:
    id: int
    amount: float

    @strawberry.field(description="The raw material or component used.")
    async def input_product(self, info: Info) -> Optional[ProductType]:
        return self.input_product

    @strawberry.field(description="The resulting product created.")
    async def output_product(self, info: Info) -> Optional[ProductType]:
        return self.output_product


@strawberry.type(description="Specific values/quantities targeted in a plan.")
class PlanValueType:
    id: int
    value: float

    @strawberry.field
    async def product(self, info: Info) -> ProductType:
        return self.product


@strawberry.type(description="Hierarchical production plans.")
class ProductionPlanType:
    id: int

    @strawberry.field(
        description="The list of specific product quantities in this plan."
    )
    async def values(self, info: Info) -> List[PlanValueType]:
        # Using the ORM relationship 'plan_values'
        return self.plan_values

    @strawberry.field(
        description="If this is a sub-plan, this points to the master plan."
    )
    async def master_plan(self, info: Info) -> Optional["ProductionPlanType"]:
        return self.master_plan
