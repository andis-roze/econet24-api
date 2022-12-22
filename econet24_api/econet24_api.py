import requests
from datetime import datetime, timedelta
from typing import List, Optional


class LoginFailed(Exception):
    pass


class Econet24APIBase:
    API_ROOT = "https://www.econet24.com"
    session: requests.Session = None
    user_devices: List = []

    def __init__(self):
        self.session = requests.session()

    def _assert_csrftoken_cookie(self):
        if not len(self.session.cookies) > 0:
            raise LoginFailed

        assert isinstance(self.session.cookies.get("csrftoken"), str)

    def _assert_session_cookie(self):
        if not len(self.session.cookies) > 0:
            raise LoginFailed

        assert isinstance(self.session.cookies.get("sessionid"), str)

    def _get(self, path, **kwargs) -> requests.Response:
        response = self.session.get(f"{self.API_ROOT}{path}", **kwargs)
        response.raise_for_status()
        return response

    def _post(self, path, **kwargs) -> requests.Response:
        response = self.session.post(f"{self.API_ROOT}{path}", **kwargs)
        response.raise_for_status()
        return response

    def login(self, username: str, password: str) -> Optional[requests.Response]:
        if self.session.cookies.get("sessionid"):
            return

        response = self._post(
            "/login/",
            data={
                "username": username,
                "password": password,
            },
        )

        self._assert_session_cookie()
        self.user_devices = self.get_user_devices().get("devices", [[]])

        return response

    def get_user_devices(self):
        self._assert_session_cookie()

        response = self._get("/service/getUserDevices")
        data = response.json()

        return data


class HistoryMixin:
    def data_history(self, start: datetime, end: datetime, uid: str=None) -> Optional[dict]:
        self._assert_session_cookie()
        if not uid and not len(self.user_devices) > 0:
            raise LoginFailed

        response = self._get(
            "/service/getHistoryParamsValues",
            params={
                "uid": uid or self.user_devices[0],
                "fromDate": start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "toDate": end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            }
        )
        data = response.json()

        return data

    def data_today(self) -> Optional[dict]:
        end = datetime.now()
        start = datetime(year=end.year, month=end.month, day=end.day, hour=0, minute=0, second=0, microsecond=0)
        return self.data_history(start=start, end=end)

    def data_yesterday(self) -> Optional[dict]:
        end = datetime.now()
        end = datetime(year=end.year, month=end.month, day=end.day, hour=23, minute=59, second=59, microsecond=999999) - timedelta(days=1)
        start = datetime(year=end.year, month=end.month, day=end.day, hour=0, minute=0, second=0, microsecond=0)
        return self.data_history(start=start, end=end)

    def data_this_week(self) -> Optional[dict]:
        end = datetime.now()
        start = datetime(year=end.year, month=end.month, day=end.day, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=end.weekday())
        return self.data_history(start=start, end=end)

    def data_prev_week(self) -> Optional[dict]:
        end = datetime.now()
        start = datetime(year=end.year, month=end.month, day=end.day, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=end.weekday() + 7)
        end = datetime(year=start.year, month=start.month, day=start.day, hour=23, minute=59, second=59, microsecond=999999) + timedelta(days=6)
        return self.data_history(start=start, end=end)

    def data_this_month(self) -> Optional[dict]:
        end = datetime.now()
        start = datetime(year=end.year, month=end.month, day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.data_history(start=start, end=end)

    def data_prev_month(self) -> Optional[dict]:
        end = datetime.now()
        end = datetime(year=end.year, month=end.month, day=1, hour=23, minute=59, second=59, microsecond=999999) - timedelta(days=1)
        start = datetime(year=end.year, month=end.month, day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.data_history(start=start, end=end)


class Econet24API(Econet24APIBase, HistoryMixin):
    pass


if __name__ == "__main__":
    from getpass import getpass

    api = Econet24API()
    api.login(username=input("Username: "), password=getpass(prompt="Password: "))
    print(api.get_user_devices())
