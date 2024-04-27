from typing import Any, Dict

import requests


def send_request(
    *,
    url: str,
    method: str,
    headers: Dict[str, str] | None = None,
    data: Dict[str, Any] | None = None,
    json: Dict[str, Any] | None = None,
    timeout: int = 10,
):
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            data=data,
            json=json,
            timeout=timeout,
        )
        response.raise_for_status()
        response_data = response.json()
        response_data["status_code"] = response.status_code
        return response_data
    except requests.exceptions.HTTPError as e:
        return {
            "status_code": e.response.status_code,
            "detail": str(e),
            "data": None,
        }
    except Exception as e:
        print("Error occurred while sending request", e)
        return {
            "status_code": 500,
            "detail": "An error occurred while sending request",
            "data": None,
        }
