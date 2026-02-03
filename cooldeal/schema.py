import graphene


class Query(graphene.ObjectType):
    hello = graphene.String(description="Retourne une salutation simple")

    def resolve_hello(parent, info):
        return "Salut depuis GraphQL"


schema = graphene.Schema(query=Query)
