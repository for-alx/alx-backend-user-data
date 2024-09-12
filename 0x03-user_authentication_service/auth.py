#!/usr/bin/env python3
"""Authentication provider
"""
import bcrypt
from uuid import uuid4
from db import DB
from sqlalchemy.orm.exc import NoResultFound
from user import User


def _hash_password(password: str) -> bytes:
    """return salted and hashed password byte
    """
    salt = bcrypt.gensalt(rounds=5)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


def _generate_uuid() -> str:
    """generate uuid
    """
    uuid_str = str(uuid4())
    return uuid_str


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Register new user into the database
        """
        # Note: NoResultFound raised if record doesn't exist only
        try:
            is_email_exist = self._db.find_user_by(email=email)
            raise ValueError(f"User {is_email_exist.email} already exists")
        except NoResultFound:
            new_user = self._db.add_user(email, _hash_password(password))
            return new_user

    def valid_login(self, email: str, password: str) -> bool:
        """validate credentials
        """
        try:
            is_user_exist = self._db.find_user_by(email=email)
            if bcrypt.checkpw(password.encode('utf-8'),
                              is_user_exist.hashed_password):
                return True
            else:
                return False
        except NoResultFound:
            return False

    def create_session(self, email: str) -> str:
        """ create and attach session token to a user
        """
        try:
            user = self._db.find_user_by(email=email)
            session_token = _generate_uuid()
            self._db.update_user(user_id=user.id, session_id=session_token)
            return session_token
        except NoResultFound:
            return None
