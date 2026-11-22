from rpms.exception.exceptions import LoginError


class UserService:
    """
    Prototype login: the user picks an existing ACTIVE username.
    The sample database only holds demo password hashes, so passwords are not
    checked here. (Real password checking is outside the scope of this project.)
    """

    def __init__(self, user_dao):
        self.user_dao = user_dao

    def get_active_users(self):
        return self.user_dao.find_all_active()

    def login(self, username):
        user = self.user_dao.find_by_username(username.strip())
        if not user:
            raise LoginError("User not found.")
        if user.status != "ACTIVE":
            raise LoginError(f"User is {user.status}. Login not allowed.")
        self.user_dao.update_last_login(user.user_id)
        return user
