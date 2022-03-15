import requests


class UserSession:
    def __init__(
        self,
        session: requests.Session,
        data: dict
    ):
        self.requests_session = session
        self.data = data