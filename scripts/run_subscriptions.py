import asyncio
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport

# Define your subscription query
subscription = gql("""
    subscription {
        newPostAdded {
            id
            title
            content
        }
    }
""")

async def main():
    # Connect to your Django Channels GraphQL endpoint
    transport = WebsocketsTransport(url="ws://localhost:8000/graphql/")

    async with Client(transport=transport, fetch_schema_from_transport=True) as session:
        async for result in session.subscribe(subscription):
            print("📩 New event received:", result)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Subscription stopped by user")
