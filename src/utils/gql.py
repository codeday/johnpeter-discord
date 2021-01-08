from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.websockets import WebsocketsTransport


class GQLService:
    @staticmethod
    def make_query(query):
        fragments = """
                fragment MemberInformation on ShowcaseMember {
                    username
                    account {
                        discordId
                    }
                }
                fragment ProjectInformation on ShowcaseProject {
                    id
                    name
                    type
                    pod: metadataValue(key: "pod")
                    description
                    members {
                        ...MemberInformation
                    }
                }
            """
        return gql(query + "\n" + fragments)

    @staticmethod
    async def subscribe_ws(query, variable_values=None):
        transport = WebsocketsTransport(
            url='ws://graph.codeday.org/subscriptions')
        session = Client(transport=transport, fetch_schema_from_transport=True)
        async for result in session.subscribe_async(GQLService.make_query(query), variable_values=variable_values):
            yield result

    @staticmethod
    async def member_removed_listener():
        query = """
            subscription {
              memberRemoved {
                  ...MemberInformation
                  project {
                      ...ProjectInformation
                  }
              }
            }
        """

        async for result in GQLService.subscribe_ws(query):
            yield result["memberRemoved"]

    @staticmethod
    async def member_added_listener():
        query = """
            subscription {
              memberAdded {
                  ...MemberInformation
                  project {
                      ...ProjectInformation
                  }
              }
            }
        """

        async for result in GQLService.subscribe_ws(query):
            yield result["memberAdded"]

    @staticmethod
    async def team_created_listener():
        query = """
            subscription {
              projectCreated {
                  ...ProjectInformation
              }
            }
        """

        async for result in GQLService.subscribe_ws(query):
            yield result["projectCreated"]

    @staticmethod
    async def team_edited_listener():
        query = """
            subscription {
              projectEdited {
                  ...ProjectInformation
              }
            }
        """

        async for result in GQLService.subscribe_ws(query):
            yield result["projectEdited"]
