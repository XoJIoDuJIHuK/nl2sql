import json
from fastapi import FastAPI, Depends, Request
from graphql import print_schema
from starlette.responses import HTMLResponse
from database import get_db
from graphene_server.schema import schema
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()


@app.get("/graphql", response_class=HTMLResponse)
async def graphiql_interface():
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <title>GraphiQL</title>
        <style>
          body { height: 100%; margin: 0; width: 100%; overflow: hidden; }
          #graphiql { height: 100vh; }
        </style>
        <!-- React -->
        <script crossorigin src="https://cdn.jsdelivr.net/npm/react@18/umd/react.production.min.js"></script>
        <script crossorigin src="https://cdn.jsdelivr.net/npm/react-dom@18/umd/react-dom.production.min.js"></script>

        <!-- GraphiQL -->
        <script crossorigin src="https://cdn.jsdelivr.net/npm/graphiql@3.0.6/graphiql.min.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/graphiql@3.0.6/graphiql.min.css" />
      </head>
      <body>
        <div id="graphiql"></div>
        <script>
          const fetcher = GraphiQL.createFetcher({
            url: '/graphql',
          });
          ReactDOM.render(
            React.createElement(GraphiQL, { fetcher: fetcher }),
            document.getElementById('graphiql'),
          );
        </script>
      </body>
    </html>
    """


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


@app.get("/graphql-schema/")
async def get_schema():
    return print_schema(schema.graphql_schema)


@app.get("/")
async def root():
    return {"message": "Use /graphql endpoint for queries"}
