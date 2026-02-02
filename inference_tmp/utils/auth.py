import os
from fastapi import Request, HTTPException

REPORT_SERVER_TOKEN = os.getenv("REPORT_SERVER_TOKEN", "")
REQUIRE_SERVER_TOKEN = os.getenv("REQUIRE_SERVER_TOKEN", "0") == "1"

def verify_server_token(request: Request):
    if not REQUIRE_SERVER_TOKEN:
        return  # 인증 비활성화 (개발용)

    token = request.headers.get("X-REPORT-SERVER-TOKEN")
    if not token or token != REPORT_SERVER_TOKEN:
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": "ACCESS_DENIED",
                "message": "Invalid or missing X-REPORT-SERVER-TOKEN"
            }
        )
