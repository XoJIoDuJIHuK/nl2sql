import asyncio
import json
import logging
import os
import sys
from contextlib import AsyncExitStack

import aiohttp
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class MCPClient:
    def __init__(self):
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self.openai = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.forbidden_tools = [
            # "list_schemas",
            # "list_objects",
            # "get_object_details",
            "explain_query",
            "analyze_workload_indexes",
            "analyze_query_indexes",
            "analyze_db_health",
            "get_top_queries",
            # "execute_sql",
        ]
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        # self.model = "deepseek/deepseek-v3.1-terminus"
        self.model = "openai/gpt-4.1-mini"
        # self.model = "openai/gpt-5"

        with open("./YYY04.md") as file:
            self.system_prompt = file.read()

    async def connect_to_server(self):
        # Configure postgres-mcp-server with connection string from env vars
        connection_string = (
            f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
            f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}?sslmode=disable"
        )
        self.logger.debug("Using connection string %s", connection_string)
        server_params = StdioServerParameters(
            command="uvx",  # Use uvx to run postgres-mcp-server
            # args=["postgres-mcp-server", connection_string],
            args=["postgres-mcp", connection_string],
            env={
                "POSTGRES_HOST": os.getenv("POSTGRES_HOST"),
                "POSTGRES_PORT": os.getenv("POSTGRES_PORT"),
                "POSTGRES_DB": os.getenv("POSTGRES_DB"),
                "POSTGRES_USER": os.getenv("POSTGRES_USER"),
                "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
            },
        )
        self.logger.debug("Server params: %s", server_params)
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.protocol = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.protocol)
        )
        await self.session.initialize()
        response = await self.session.list_tools()
        tools = [
            tool.name
            for tool in response.tools
            if tool.name not in self.forbidden_tools
        ]
        print("\nConnected to postgres mcp server with tools:", tools)

    async def call_local_http_server(self, args: dict) -> str:
        base_url = "http://localhost:8000"  # Change if your server is elsewhere
        endpoint = args["endpoint"]
        method = args["method"].upper()
        data = json.loads(args["data"]) if args["data"] != "" else {}

        try:
            async with aiohttp.ClientSession() as session:
                url = base_url + endpoint
                if method == "GET":
                    async with session.get(url, params=data) as resp:
                        if resp.status == 200:
                            return await resp.text()
                        else:
                            return f"HTTP error: {resp.status} - {await resp.text()}"
                elif method == "POST":
                    async with session.post(url, json=data) as resp:
                        if resp.status == 200:
                            return await resp.text()
                        else:
                            return f"HTTP error: {resp.status} - {await resp.text()}"
                else:
                    return "Unsupported HTTP method"
        except Exception as e:
            self.logger.error(f"HTTP call failed: {str(e)}")
            return f"Error during HTTP call: {str(e)}"

    async def process_query(self, query: str) -> str:
        # system_prompt = (
        #     "You are assistant capable of querying the database "
        #     "and providing info based on its contents. Use neccessary "
        #     "tools provided. You may execute select queries using "
        #     "respective tool. Before making resulting queries to "
        #     "the database, inspect its schema and objects to understand "
        #     "user's request. User may use synonyms or names not used "
        #     "in the database and your task is to understand that "
        #     "and produce valid queries. If the user's query is ambiguos, "
        #     "ask for clarification. "
        #     "The context of the database is following: there's cluster "
        #     "of producers. Each producer produces range of products (sets "
        #     "of products may intersect). Prerequisites of each product "
        #     "maybe empty or include some other products which is displayed "
        #     "in the database. There's plan on how much of each product "
        #     "to produce. Your task is to answer user's questions about "
        #     "objects and data in the database"
        # )
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query},
        ]
        if self.session is None:
            raise ValueError("Session is None")
        response = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in response.tools
            if tool.name not in self.forbidden_tools
        ]
        # available_tools.append(
        #     {
        #         "type": "function",
        #         "function": {
        #             "name": "call_local_http_server",
        #             "description": "Call a local HTTP server to retrieve some data. Must be used with body and query parameters",
        #             "parameters": {
        #                 "type": "object",
        #                 "properties": {
        #                     "endpoint": {
        #                         "type": "string",
        #                         "description": "The API endpoint to call: for now only '/process' is available",
        #                     },
        #                     "method": {
        #                         "type": "string",
        #                         "description": "HTTP method: for now only POST is available",
        #                     },
        #                     "data": {
        #                         "type": "string",
        #                         "description": "JSON-stringified data to send in the request body for POST requests or JSON-stringified dictionary of query parameters to send in the request URL for GET requests. May be empty",
        #                     },
        #                 },
        #                 "required": ["endpoint", "method", "data"],
        #             },
        #         },
        #     },
        # )
        self.logger.debug(
            "Available tools: %s",
            json.dumps(
                [
                    {"name": tool.name, "description": tool.description}
                    for tool in response.tools
                ],
                indent=2,
            ),
        )

        # Initial LLM call
        self.logger.debug("Sending initial LLM request with messages: %s", messages)
        response = self.openai.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=available_tools or None,
            max_tokens=1000,
        )
        self.logger.debug("Initial LLM response: %s", response)

        final_text = []
        while True:
            # LLM call
            self.logger.debug("Sending LLM request with messages: %s", messages)
            response = self.openai.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=available_tools or None,
                max_tokens=1000,
            )
            self.logger.debug("LLM response: %s", response)

            assistant_message = response.choices[0].message
            assistant_content = assistant_message.content or ""
            tool_calls = assistant_message.tool_calls

            self.logger.debug("Tool calls: %s", tool_calls)

            if tool_calls:
                # Append the full assistant message, including tool_calls
                messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": tc.type,
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in tool_calls
                        ],
                    }
                )

                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        self.logger.error(
                            "Invalid JSON in tool arguments: %s",
                            tool_call.function.arguments,
                        )
                        tool_args = {}  # Fallback to empty dict or handle error

                    self.logger.debug(
                        "LLM calling tool: %s with args: %s", tool_name, tool_args
                    )
                    if tool_name == "call_local_http_server":
                        # NEW: Handle custom tool separately
                        __import__("pdb").set_trace()
                        tool_result_content = await self.call_local_http_server(
                            tool_args
                        )
                    else:
                        # Existing MCP tool handling
                        result = await self.session.call_tool(tool_name, tool_args)
                        self.logger.debug(
                            "Tool result for %s: %s", tool_name, result.content
                        )
                        tool_result_content = (
                            result.content[0].text
                            if isinstance(result.content, list) and result.content
                            else str(result.content)
                        )
                    self.logger.debug(
                        "Tool result for %s: %s", tool_name, tool_result_content
                    )

                    messages.append(
                        {
                            "role": "tool",
                            "content": tool_result_content,
                            "tool_call_id": tool_call.id,
                        }
                    )
                # Continue the loop for another LLM call
            else:
                # No more tool calls, this is the final response
                final_text.append(assistant_content)
                break

        final_response = "\n".join(final_text).strip()
        self.logger.debug(
            "Final generated response (SQL or message): %s", final_response
        )
        return final_response

    async def chat_loop(self):
        print("\nNL2SQL System Started! Type 'quit' to exit.")
        while True:
            query = input("\nNL Query: ").strip()
            if query.lower() == "quit":
                break
            response = await self.process_query(query)
            print("\nAnswer:\n" + response)

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
