"""Short-code generation."""
import secrets
import string

ALPHABET = string.ascii_letters + string.digits


def new_code(length: int = 7) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
