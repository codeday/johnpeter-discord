import json
from jwt import encode
import time
import requests
from os import getenv


def gql_token():
    secret = getenv("GQL_ACCOUNT_SECRET")
    message = {
        "scopes": "write:users",
        "exp": int(time.time()) + (60*60*24)
    }
    return encode(message, secret, algorithm='HS256').decode("utf-8")


def gql(query):
    result = requests.post("https://graph.codeday.org/",
                           json={"query": query},
                           headers={"Authorization": f"Bearer {gql_token()}"})
    data = json.loads(result.text)
    if "errors" in data:
        print(data["errors"])
    return data["data"]


def get_username(member):
    query = f"""{{
        account {{
            getUser(where: {{ discordId: "{member.id}" }}) {{
                username
            }}
        }}
    }}"""
    user = gql(query)["account"]["getUser"]
    if user:
        return user["username"]
    return None


async def grant(bot, member, id):
    print(f"granting badge {id}...")
    username = get_username(member)
    if not username:
        return False
    print(f"...to {username}")

    query = f"""mutation {{
        account {{
            grantBadge(username: "{username}", badge: {{ id: "{id}" }})
        }}
    }}"""

    gql(query)

    channel = await bot.fetch_channel(int(getenv("CHANNEL_A_UPDATE")))
    await channel.send(f"a~update <@{member.id}>")

    return True
