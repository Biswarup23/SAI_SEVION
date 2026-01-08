import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class ApiClient:
    def __init__(self):
        self.http = requests.Session()
        retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        self.http.mount("http://", adapter)
        self.http.mount("https://", adapter)

    def post(self, url: str, payload: dict, headers=None, timeout=15):
        return self.http.post(url, json=payload, headers=headers or {}, timeout=timeout)

api = ApiClient()
