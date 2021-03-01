import json
from jwt import encode
import time
import requests
import logging
from os import getenv


def gql_token():
    secret = getenv("GQL_ACCOUNT_SECRET")
    message = {
        "scopes": "write:users",
        "exp": int(time.time()) + (60 * 60 * 24)
    }
    return encode(message, secret, algorithm='HS256').decode("utf-8")


def gql(query):
    result = requests.post("https://graph.codeday.org/",
                           json={"query": query},
                           headers={"Authorization": f"Bearer {gql_token()}"})
    data = json.loads(result.text)
    if "errors" in data:
        # logging.error(result.text)
        raise Exception(data["errors"][0]["message"])
    return data["data"]


def get_username(member):
    query = f"""{{
        account {{
            getUser(where: {{ discordId: "{member.id}" }}) {{
                username
            }}
        }}
    }}"""
    result = gql(query)
    try:
        user = result["account"]["getUser"]
        if user:
            return user["username"]
    except:
        logging.error(
            f"could not look up ${member.id}")
        pass
    return None


async def choose_cult(ctx, member, id):
    id = id.lower()
    if id != "pizza" and id != "turtle":
        return False
    username = get_username(member)
    if not username:
        return False
    logging.info(f"granting badge {id} to {username}")
    query = f"""mutation {{
        account {{
            pizzaOrTurtleCult(where: {{username: "{username}"}}, pizzaOrTurtle: {id.upper()})
        }}
    }}"""
    try:
        gql(query)
        return True
    except Exception as e:
        await ctx.send(str(e))
        return False


async def grant(member, id):
    logging.info(f"granting badge {id}...")
    username = get_username(member)
    if not username:
        return False
    logging.info(f"...to {username}")

    query = f"""mutation {{
        account {{
            grantBadge(where: {{username: "{username}"}}, badge: {{ id: "{id}" }})
        }}
    }}"""

    gql(query)

    return True
