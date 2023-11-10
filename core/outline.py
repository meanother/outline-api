import requests
import urllib3
import json
from pathlib import Path
import time

from requests.adapters import HTTPAdapter, Retry
from typing import Union, Optional

from core.utils import logger, get_dt, read_outline_config
from core.db import insert, select_user, update_user_limit, delete_user

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


retries = Retry(
    total=3,
    backoff_factor=0.250,
    status_forcelist=[500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retries)
headers = {'Content-Type': 'application/json'}

MASK = "#"


def load_config() -> dict:
    config_path = Path(__file__).resolve().parent.parent / "config.json"
    if config_path.exists():
        with open(config_path, "r") as conf_file:
            data = json.load(conf_file)
        return data
    else:
        raise FileNotFoundError("Check config.json in base dir")


class OutlineBackend:

    def __init__(self):
        self.session = requests.Session()
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.server = read_outline_config()
        self.base_url = self.server["apiUrl"]

    def _get(self, path: str):
        url = f"{self.base_url}/{path}"
        response = self.session.request("GET", url, verify=False, headers=headers)
        if response.status_code == 200:
            return response.json()

    def _post(self, path: str, data=None):
        url = f"{self.base_url}/{path}"
        response = self.session.request("POST", url, verify=False, headers=headers, data=data)

        if response.status_code == 201:
            return response.json()

    def _put(self, path: str, data=None):
        url = f"{self.base_url}/{path}"
        json_data = json.dumps(data)
        response = self.session.put(url, verify=False, headers=headers, data=json_data)

        if response.status_code == 204:
            return

    def _delete(self, path: str):
        url = f"{self.base_url}/{path}"
        response = self.session.delete(url, verify=False, headers=headers)

        if response.status_code == 204:
            return

    def get_server(self):
        return self._get("server")

    def get_metrics(self):
        return self._get("metrics/enabled")

    def get_all_keys(self):
        return self._get("access-keys")

    def rename_key(self, key_id: Union[str, int], key_name: str):
        return self._put(f"access-keys/{key_id}/name", data={"name": key_name})

    @staticmethod
    def get_user(username: str) -> Optional[dict]:
        logger.info(f"get info from sqlite3 for user: {username}")
        data = select_user(username)
        return data

    def get_user_info(self, key_id: Union[str, int]) -> dict:
        response = self.get_all_keys()
        for key in response.get("accessKeys"):
            if str(key.get("id")) == str(key_id):
                data = {
                    "key_id": key.get("id"),
                    "name": key.get("name"),
                    "password": key.get("password"),
                    "server_port": key.get("port"),
                    "method": key.get("method"),
                    "access_url": key.get("accessUrl") + MASK,
                    "data_limit": key.get("dataLimit").get("bytes")
                    / 1000 / 1000 / 1000 if key.get("dataLimit") else None,
                    "create_dt": get_dt(),
                }
                return data
        return {}

    def create_new_key(self, name: str, limit: str) -> dict:
        if_exists = self.get_user(name)
        if if_exists:
            return {"error": f"user {name} already exists"}

        response = self._post("access-keys")
        key_id = response.get("id")

        time.sleep(0.25)

        self.rename_key(key_id, name)
        user_info = self.get_user_info(key_id)
        insert("outline_users", user_info)
        self.set_data_limit(user_info['name'], str(limit))
        return user_info

    def set_data_limit(self, username: Union[str, int], size: str):
        user_key = self.get_user(username)
        update_user_limit(username, str(size))
        self._put(
            f"access-keys/{user_key['key_id']}/data-limit",
            data={"limit": {"bytes": int(size) * 1000 * 1000 * 1000}}
        )
        logger.info(f"set data limit to {size} for user {username}")
        return {"username": username, "limit": size}

    def set_infinity_limit(self, key_id: Union[str, int]):
        logger.info(f"Setup unlimited data to {key_id}")
        return self._delete(f"access-keys/{key_id}/data-limit")

    def disable_user(self, username: Union[str, int]) -> dict:
        logger.info(f"Setup data limit `0` to {username}")
        # user_key = self.get_user(username)
        self.set_data_limit(username, "0")
        return {"username": username, "status": "disable"}

    def enable_user(self, username: Union[str, int]):
        user_key = self.get_user(username)
        self.set_infinity_limit(user_key["key_id"])

    def delete_key(self, username: Union[str, int]) -> dict:
        user_key = self.get_user(username)
        logger.info(f"Delete username: {username}")
        self._delete(f"access-keys/{user_key['key_id']}")
        delete_user(username)
        return {"username": username, "status": "deleted"}
