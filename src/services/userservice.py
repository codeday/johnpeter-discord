from database.users import User
from .database import Database


class UserDatabase(Database):
    def get_user(self, user: User):
        query = (f"SELECT discord_id from discord_users "
                 f"WHERE discord_id = {user.discord_id}")
        with self:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
        if result:
            return User(result[0], result[1])
        else:
            return False

    def create_user(self, user: User):
        if not self.get_user(user):
            self.add_row(table='discord_users',
                         headers=['discord_id', 'clear_username'],
                         values=[user.discord_id, user.clear_username])
        return