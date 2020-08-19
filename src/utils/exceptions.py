from discord.ext.commands import Context


class BugReport(Exception):
    """Raised when a user submits a bug report"""

    def __init__(
        self, message="unknown", context: Context = None
    ):
        self.message = message
        if context is not None:
            self.context = context
        super().__init__(self.message)

    def __str__(self):
        if self.context is not None:
            return f"Bug report: {self.message}, channel: {self.context.channel.name}"
        else:
            return f"Bug report: {self.message}"
