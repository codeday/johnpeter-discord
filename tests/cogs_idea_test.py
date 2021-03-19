import pytest

from cogs.idea import IdeaCog

cog = IdeaCog(bot=None)


@pytest.mark.asyncio
async def test_idea_generate():
    for i in range(100):
        assert type(cog.generate_idea()) is str
