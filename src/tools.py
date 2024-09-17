import jwt
import time
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, DecodeError
from config import settings


def check_token(token: str):
    try:
        decoded_token = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm_hash])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except (ExpiredSignatureError, InvalidSignatureError, DecodeError):
        return {}
