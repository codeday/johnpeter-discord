from database.users import User
from .database import Database


class UserDatabase(Database):
    def get_user(self, user: User):
        query = (f"SELECT discord_id from {self.database}.discord_users "
                 f"WHERE discord_id = {user.discord_id};")
        with self:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
        if result:
            return User(result[0], result[1])
        else:
            return False

    def create_user(self, user: User):
        if not self.get_user(user):
            self.add_row(table=f'{self.database}.discord_users',
                         headers=['discord_id', 'clear_username'],
                         values=[user.discord_id, user.clear_username])
        return

    def update_user(self, user):
        u = self.get_user(user)
        if u != user:
            exc = (f"UPDATE {self.database}.discord_users ",
                   f"SET clear_username = '{user.clear_username}' ",
                   f"WHERE clear_username = '{u.clear_username}';")
