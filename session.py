from flask import session as flask_session

class Session:
    def __init__(self):
        self._is_authenticated = False

    @property
    def is_authenticated(self):
        print("is_authenticated property called")
        return self._is_authenticated

    @property
    def username(self):
        return flask_session.get('username')

    def login(self, username):
        print("login method called with username:", username)
        flask_session['username'] = username
        self._is_authenticated = True
        print("_is_authenticated set to:", self._is_authenticated)

    def logout(self):
        flask_session.pop('username', None)
        self._is_authenticated = False

    def print_session(self):
        print(f"session['username']={flask_session.get('username')}, is_authenticated={self._is_authenticated}")

