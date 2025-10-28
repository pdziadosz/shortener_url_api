import base64
import hashlib
import random
import string


def generate_unique_code_from_id(
    obj_id: int, code_length: int = 8, salt_length: int = 4
) -> str:
    salt = "".join(random.choices(string.ascii_letters + string.digits, k=salt_length))
    combined = f"{obj_id}{salt}"
    hash_bytes = hashlib.sha256(combined.encode()).digest()
    b64_code = base64.urlsafe_b64encode(hash_bytes).decode("utf-8")
    return b64_code[:code_length]
