import json
import time
import random
from typing import Dict, Any, Optional, List
from datetime import datetime

import requests
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse

app = FastAPI()

TARGET_API = "http://203.18.158.95:8000/get"


# ==================== CORE ====================
class FreeFireProxy:

    def __init__(self):
        self.total_request = 0
        self.success = 0
        self.error = 0
        self.last_requests: List[Dict[str, Any]] = []

    def log(self, data: Dict[str, Any]):
        self.last_requests.append(data)
        if len(self.last_requests) > 20:
            self.last_requests.pop(0)

    def stats(self):
        total = max(self.total_request, 1)
        return {
            "total_request": self.total_request,
            "success": self.success,
            "error": self.error,
            "success_rate": f"{(self.success / total) * 100:.1f}%",
            "last_requests": self.last_requests
        }

    def build_params(self, access, jwt_token, itemid):
        params = {}

        if access:
            params["access"] = access
        if jwt_token:
            params["jwt_token"] = jwt_token

        params["itemid"] = itemid
        return params

    def validate(self, access, jwt_token, itemid):
        if not access and not jwt_token:
            return False, "Thiếu access hoặc jwt_token"

        if not itemid or len(itemid) == 0:
            return False, "Thiếu itemid"

        if len(itemid) > 50:
            return False, "Quá nhiều itemid (max 50)"

        return True, None

    def call_api(self, params):
        try:
            res = requests.get(TARGET_API, params=params, timeout=10)
            try:
                return res.json()
            except:
                return {"raw": res.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}


proxy = FreeFireProxy()


# ==================== ROOT ====================
@app.get("/")
def root():
    return {
        "api_endpoint": "ADD ITEMS ACCESS TOKEN TO JWT",
        "examples": {
            "using_access": "/get?access=xxx&itemid=211000000&itemid=211000000",
            "using_jwt": "/get?jwt_token=xxx&itemid=211000000&itemid=211000000"
        },
        "message": "API BY RIO 𝕏 LUANORI⚡",
        "status": "running",
        "usage": "Use /get with either 'access' (to convert) or 'jwt_token' (direct) plus 15 itemid parameters."
    }


# ==================== MAIN API ====================
@app.get("/get")
def get_items(
    request: Request,
    access: str = None,
    jwt_token: str = None,
    itemid: List[str] = Query(default=[])
):
    proxy.total_request += 1

    valid, error_msg = proxy.validate(access, jwt_token, itemid)

    if not valid:
        proxy.error += 1
        return JSONResponse({
            "status": "error",
            "message": error_msg
        }, status_code=400)

    params = proxy.build_params(access, jwt_token, itemid)

    start = time.time()
    result = proxy.call_api(params)
    end = time.time()

    log_data = {
        "time": datetime.now().isoformat(),
        "ip": request.client.host if request.client else "unknown",
        "items": len(itemid),
        "exec_time": round(end - start, 3)
    }

    proxy.log(log_data)

    if result.get("status") == "success":
        proxy.success += 1
    else:
        proxy.error += 1

    return result


# ==================== STATS ====================
@app.get("/stats")
def stats():
    return proxy.stats()


# ==================== HEALTH ====================
@app.get("/health")
def health():
    return {
        "status": "ok",
        "time": datetime.now().isoformat()
    }