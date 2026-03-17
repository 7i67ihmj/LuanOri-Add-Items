import requests
import time
import random
from typing import List, Optional
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse

# ================= CONFIG =================
TARGET_API = "http://203.18.158.95:8000/get"
TIMEOUT = 10
MAX_RETRY = 3

HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
        "Accept": "*/*",
        "Connection": "keep-alive"
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*"
    }
]

# ================= APP =================
app = FastAPI(title="LUANORI API", version="3.0")

# ================= LOGGER =================
class Logger:
    @staticmethod
    def log(msg):
        print(f"[LOG] {msg}")

    @staticmethod
    def error(msg):
        print(f"[ERROR] {msg}")


# ================= CORE CLIENT =================
class APIClient:
    def __init__(self):
        self.session = requests.Session()

    def get_headers(self):
        return random.choice(HEADERS_LIST)

    def send_request(self, params: dict):
        for attempt in range(MAX_RETRY):
            try:
                Logger.log(f"Try {attempt+1} gửi request...")
                r = self.session.get(
                    TARGET_API,
                    params=params,
                    headers=self.get_headers(),
                    timeout=TIMEOUT
                )

                Logger.log(f"Status: {r.status_code}")

                if r.status_code == 200:
                    try:
                        return r.json()
                    except:
                        return {"raw": r.text}

                time.sleep(1)

            except Exception as e:
                Logger.error(str(e))
                time.sleep(1)

        return {
            "status": "error",
            "message": "Request thất bại sau nhiều lần thử"
        }


client = APIClient()

# ================= ROUTES =================

@app.get("/")
def root():
    return {
        "api_endpoint": "ADD ITEMS ACCESS TOKEN TO JWT",
        "examples",
        "using_access": "/get?access=xxx&itemid=211000000&itemid=211000000",
        "using_jwt": "/get?jwt_token=xxx&itemid=211000000&itemid=211000000",
        "message": "API BY RIO 𝕏 LUANORI⚡",
        "status": "running",
        "usage": "Use /get with either 'access' (to convert) or 'jwt_token' (direct) plus 15 itemid parameters."
    }


@app.get("/get")
def get_items(
    access: Optional[str] = None,
    jwt_token: Optional[str] = None,
    itemid: List[str] = Query(default=[])
):
    if not access and not jwt_token:
        return JSONResponse(
            {"status": "error", "message": "Thiếu access hoặc jwt_token"},
            status_code=400
        )

    if len(itemid) == 0:
        return JSONResponse(
            {"status": "error", "message": "Thiếu itemid"},
            status_code=400
        )

    params = {}

    if access:
        params["access"] = access

    if jwt_token:
        params["jwt_token"] = jwt_token

    params["itemid"] = itemid

    Logger.log(f"Params: {params}")

    result = client.send_request(params)

    return result


# ================= HEALTH =================
@app.get("/health")
def health():
    return {"status": "ok"}


# ================= VERCEL HANDLER =================
def handler(request: Request):
    return app(request.scope, request.receive, request.send)