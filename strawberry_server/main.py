from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry_server.graphql.schema import schema

app = FastAPI()

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    return {"message": "Go to /graphql to access the GraphiQL interface"}

@app.get('/graphql-schema')
async def get_schema():
    introspection_query = """
        query IntrospectionQuery {
          __schema {
            queryType { name }
            mutationType { name }
            subscriptionType { name }
            types {
              ...FullType
            }
            directives {
              name
              description
              locations
              args(includeDeprecated: true) {
                ...InputValue
              }
            }
          }
        }

        fragment FullType on __Type {
          kind
          name
          description
          fields(includeDeprecated: true) {
            name
            description
            args(includeDeprecated: true) {
              ...InputValue
            }
            type {
              ...TypeRef
            }
            isDeprecated
            deprecationReason
          }
          inputFields(includeDeprecated: true) {
            ...InputValue
          }
          interfaces {
            ...TypeRef
          }
          enumValues(includeDeprecated: true) {
            name
            description
            isDeprecated
            deprecationReason
          }
          possibleTypes {
            ...TypeRef
          }
        }

        fragment InputValue on __InputValue {
          name
          description
          type { ...TypeRef }
          defaultValue
          isDeprecated
          deprecationReason
        }

        fragment TypeRef on __Type {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                        ofType {
                          kind
                          name
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
    """

    result = await schema.execute(introspection_query)
    return result.data
