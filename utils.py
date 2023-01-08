from datetime import datetime
import requests
import jwt


def get_order_status(token):
    url = "https://owner-api.teslamotors.com/api/1/users/orders"
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


# check if token is expired
def is_token_expired(token, now=None):
    if now is None:
        now = datetime.now()
    try:
        jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_iat": True,
                "verify_exp": True,
            },
        )
        return False
    except jwt.ExpiredSignatureError:
        return True


# refresh new token
def get_new_token(token, refresh_token):
    if not is_token_expired(token):
        return {
            "access_token": token,
            "refresh_token": refresh_token,
        }
    url = "https://auth.tesla.com/oauth2/v3/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": "ownerapi",
        "refresh_token": refresh_token,
        "scope": "openid email offline_access",
    }
    headers = {"Authorization": "Bearer " + token}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def notify(msg, line_token):
    line_url = "https://notify-api.line.me/api/notify"
    line_headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + line_token,
    }
    requests.post(line_url, headers=line_headers, data={"message": msg})
