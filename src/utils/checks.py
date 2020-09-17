from discord.ext.commands import Context, check, MissingAnyRole
from json import loads
from os import getenv


def requires_staff_role():
    """A check that scans for a staff role. Staff roles must be updated here, which isn't that obvious,
    but it will try to pull from env vars, then fall back to the staff role listed.
    """
    async def predicate(ctx: Context):
        # Current "Staff" and "Employee" roles ID as of 9/17/20
        staff_id = loads(getenv("ROLES_STAFF", '["689215241996730417", "712062910897061979"]'))
        if [i for i in [str(role.id) for role in ctx.author.roles] if i in staff_id]:
            return True
        raise MissingAnyRole(staff_id)
    return check(predicate)


def requires_tournament_role():
    """A check that scans for a tournament-related role. Roles must be updated here, which isn't that obvious,
    but it will try to pull from env vars, then fall back to the roles listed.
    """
    async def predicate(ctx: Context):
        # Current "Tournament Leader" and "Employee" role IDs as of 9/17/20
        staff_id = loads(getenv("ROLES_TOURNAMENT", '["693206115349037069", "712062910897061979"]'))
        if [i for i in [str(role.id) for role in ctx.author.roles] if i in staff_id]:
            return True
        raise MissingAnyRole(staff_id)
    return check(predicate)
