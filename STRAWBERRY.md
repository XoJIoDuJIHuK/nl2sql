# Strawberry Server - GraphQL Query Processing

## Overview

The `strawberry_server` package provides a GraphQL API built with [Strawberry](https://strawberry.rocks/) (a Python GraphQL library) and [FastAPI](https://fastapi.tiangolo.com/). It exposes the database models through a GraphQL schema that allows clients to query production planning data.

## GraphQL Endpoint

### Endpoint Configuration

**Location**: `strawberry_server/main.py`

The GraphQL endpoint is mounted as a FastAPI route:

```python
app = FastAPI()

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")
```

### Making Requests

**URL**: `POST http://localhost:8000/graphql`

**Request body format**:
```json
{
  "query": "query { producers { id code } }",
  "variables": {},
  "operationName": null
}
```

**Introspection**: The schema can be explored at `/graphql-schema` or using tools like GraphiQL or Apollo Studio.

---

## Query Processing Flow

```
┌─────────────────┐
│  Client Request │
│  (POST /graphql)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI Route │
│   (GraphQLRouter)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Strawberry    │
│   - Parses query│
│   - Validates   │
│   - Executes    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Resolver      │
│   Functions     │
│   (schema.py)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   SQLAlchemy    │
│   Query Build   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│   Execution     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Response      │
│   (GraphQL JSON)│
└─────────────────┘
```

### Step-by-Step Breakdown

1. **Request Reception**: FastAPI receives the POST request at `/graphql`
2. **Routing**: The `GraphQLRouter` forwards the request to Strawberry
3. **Query Parsing**: Strawberry parses the GraphQL query and validates it against the schema
4. **Resolver Execution**: For each field in the query, Strawberry calls the corresponding resolver function
5. **Database Query**: The resolver builds a SQLAlchemy query and executes it
6. **Result Assembly**: Results are converted to GraphQL types and returned as JSON

---

## Schema and Resolvers

**Location**: `strawberry_server/graphql/schema.py`

### Available Queries

| Query | Description | Filtering |
|-------|-------------|-----------|
| `abstract_products` | All product categories | None |
| `abstract_product(id)` | Single category by ID | Primary key |
| `producers` | All producers | None |
| `producer(id)` | Producer by ID | Primary key |
| `producer_by_code(code)` | Producer by code | Unique field |
| `products` | All products | `producer_code` (optional) |
| `product(id)` | Single product by ID | Primary key |
| `production_chains` | All production chains | None |
| `production_chain(id)` | Single chain by ID | Primary key |
| `plans` | All production plans | None |
| `plan(id)` | Single plan by ID | Primary key |
| `plan_values` | All plan values | None |
| `plan_values_for_plan(plan_id)` | Values for a specific plan | Foreign key |
| `plan_values_for_product(product_id)` | Values for a specific product | Foreign key |

### Example Resolver

```python
@strawberry.field(description="Get a list of all products. Optional: filter by producer code.")
async def products(self, producer_code: str | None = None) -> list[ProductType]:
    # Build base query with eager loading of relationships
    query = select(Product).options(
        selectinload(Product.producer),
        selectinload(Product.abstract_product)
    )

    # Apply filter if provided (database-side filtering!)
    if producer_code:
        query = query.join(Product.producer).where(Producer.code == producer_code)

    # Execute query
    async for session in get_db():
        result = await session.execute(query)

    return list(result.scalars().all())
```

---

## Your Efficiency Questions Answered

### Question: Does Strawberry fetch all rows and then filter them in-memory?

**Answer: NO** (for the implemented filter) - but there are other efficiency concerns.

#### Filtering Efficiency

**What you suspected**: Fetch all rows → Load into memory → Filter in Python → Return results

**What actually happens**:
```python
# The filter is applied in the SQL query, NOT in Python
if producer_code:
    query = query.join(Product.producer).where(Producer.code == producer_code)
```

This generates SQL like:
```sql
SELECT products.* FROM products
JOIN producers ON products.producer_id = producers.id
WHERE producers.code = :producer_code
```

The filtering happens **in the database**, not in Python. Only matching rows are transferred over the network and loaded into memory.

#### The Real Efficiency Problem: No Pagination

**Current behavior**:
```python
# All matching rows are returned - no LIMIT, no OFFSET
return list(result.scalars().all())
```

If you have 10,000 products in the database, **all 10,000 rows** are:
1. Fetched from the database
2. Transferred over the network
3. Loaded into memory
4. Serialized to JSON
5. Returned to the client

This is inefficient because:
- Most clients don't need all the data at once
- Large responses increase latency
- Memory usage scales with dataset size
- Unnecessary database and network load

---

## Current Implementation Analysis

### What's Efficient ✓

1. **Database-level filtering**: The `producer_code` filter is applied in SQL
2. **Eager loading**: Uses `selectinload()` to avoid N+1 query problems
3. **Async operations**: Uses `asyncpg` for non-blocking database access
4. **Connection pooling**: Database connections are reused

### What's Inefficient ✗

1. **No pagination**: All records are always returned
2. **Limited filtering**: Only one filter across all list queries
3. **No sorting**: Cannot control result ordering
4. **No field selection**: Always returns all fields (though GraphQL itself handles this)

---

## Recommended Improvements

### 1. Add Pagination

```python
@strawberry.field
async def products(
    self,
    producer_code: str | None = None,
    limit: int = 100,
    offset: int = 0
) -> list[ProductType]:
    query = select(Product).options(
        selectinload(Product.producer),
        selectinload(Product.abstract_product)
    )

    if producer_code:
        query = query.join(Product.producer).where(Producer.code == producer_code)

    query = query.limit(limit).offset(offset)

    async for session in get_db():
        result = await session.execute(query)

    return list(result.scalars().all())
```

### 2. Add Sorting

```python
@strawberry.field
async def products(
    self,
    producer_code: str | None = None,
    order_by: str | None = None,  # "name", "-name", "id", etc.
) -> list[ProductType]:
    query = select(Product).options(...)

    if producer_code:
        query = query.join(Product.producer).where(Producer.code == producer_code)

    if order_by:
        if order_by.startswith("-"):
            query = query.order_by(desc(order_by[1:]))
        else:
            query = query.order_by(order_by)

    async for session in get_db():
        result = await session.execute(query)

    return list(result.scalars().all())
```

### 3. Consider Relay-style Connections

For a more sophisticated pagination approach, implement the [Relay Cursor Connections specification](https://relay.dev/graphql/connections.htm):

```python
@strawberry.field
async def products(
    self,
    first: int | None = None,
    after: str | None = None,
) -> Connection[ProductType]:
    # Returns edges, pageInfo, and uses cursors for pagination
    ...
```

---

## Summary

### Your Assumptions

| Assumption | Correct? | Details |
|------------|----------|---------|
| Strawberry provides POST endpoint | ✓ Yes | Standard GraphQL POST at `/graphql` |
| Takes complex body | ✓ Yes | GraphQL query, variables, operationName |
| Result from schema properties | ✓ Yes | Resolvers return data from database |
| Fetches all rows then filters | ✗ No | Filtering is done in SQL via `.where()` |
| Extremely inefficient | △ Partially | No pagination is the real issue |

### Key Takeaways

1. **Filtering is efficient**: Database-side filtering via SQLAlchemy's `.where()`
2. **Pagination is missing**: All rows are returned - this is the main scalability issue
3. **N+1 queries are avoided**: Eager loading with `selectinload()`
4. **Async is used**: Non-blocking database operations

The current implementation works well for small-to-medium datasets but would benefit from pagination, additional filters, and sorting options for production use with large datasets.
