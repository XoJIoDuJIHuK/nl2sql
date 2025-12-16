from fastapi import FastAPI, Depends, Request
from graphene_server.database import get_db
from graphene_server.schema import schema
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()


@app.post("/graphql")
async def query_graphql(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Get JSON body
    data = await request.json()
    query = data.get("query")
    variables = data.get("variables")

    # Execute Graphene Query
    # We pass the AsyncSession into the context_value so resolvers can use it
    result = await schema.execute_async(
        query,
        variable_values=variables,
        context_value={"session": db, "request": request},
    )

    if result.errors:
        return {"data": result.data, "errors": [str(error) for error in result.errors]}

    return {"data": result.data}


@app.get("/")
async def root():
    return {"message": "Use /graphql endpoint for queries"}
