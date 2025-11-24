import asyncio
import json
import os

from agent.clients.custom_mcp_client import CustomMCPClient
from agent.clients.dial_client import DialClient
from agent.clients.mcp_client import MCPClient
from agent.models.message import Message, Role


async def main():
    #TODO:
    # 1. Take a look what applies DialClient
    # 2. Create empty list where you save tools from MCP Servers later
    # 3. Create empty dict where where key is str (tool name) and value is instance of MCPClient or CustomMCPClient
    # 4. Create UMS MCPClient, url is `http://localhost:8006/mcp` (use static method create and don't forget that its async)
    # 5. Collect tools and dict [tool name, mcp client]
    # 6. Do steps 4 and 5 for `https://remote.mcpservers.org/fetch/mcp`
    # 7. Create DialClient, endpoint is `https://ai-proxy.lab.epam.com`
    # 8. Create array with Messages and add there System message with simple instructions for LLM that it should help to handle user request
    # 9. Create simple console chat (as we done in previous tasks)
    tools = []
    tool_dict = {}
    mcp_client= await MCPClient.create(mcp_server_url='http://localhost:8006/mcp')
    custom_mcp_client = await CustomMCPClient.create(mcp_server_url='https://remote.mcpservers.org/fetch/mcp')
    for tool in await mcp_client.get_tools():
       tools.append(tool)
       tool_dict[tool.get('function', {}).get('name')] = mcp_client
       print(f"{json.dumps(tool, indent=2)}")

    for tool in await custom_mcp_client.get_tools():
        tools.append(tool)
        tool_dict[tool.get('function', {}).get('name')] = custom_mcp_client
        print(f"{json.dumps(tool, indent=2)}")

    for tool in await mcp_client.get_tools():
       tools.append(tool)
       tool_dict[tool.get('function', {}).get('name')] = mcp_client
       print(f"{json.dumps(tool, indent=2)}")

    dial_client = DialClient(
        api_key=os.getenv("DIAL_API_KEY"),
        endpoint="https://ai-proxy.lab.epam.com",
        tools=tools,
        tool_name_client_map=tool_dict
    )

    messages: list[Message] = [
        Message(
            role=Role.SYSTEM,
            content="You are an advanced AI agent. Your goal is to assist user with his questions."
        )
    ]

    print("MCP-based Agent is ready! Type your query or 'exit' to exit.")
    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() == 'exit':
            break

        messages.append(
            Message(
                role=Role.USER,
                content=user_input
            )
        )

        ai_message: Message = await dial_client.get_completion(messages)
        messages.append(ai_message)


if __name__ == "__main__":
    asyncio.run(main())


# Check if Arkadiy Dobkin present as a user, if not then search info about him in the web and add him