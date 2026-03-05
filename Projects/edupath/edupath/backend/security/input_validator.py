import re
import bleach
from typing import Tuple

class InputValidator:
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 500) -> str:
        if not input_str:
            return ""

        cleaned = bleach.clean(input_str, tags=[], strip=True)
        cleaned = cleaned[:max_length]
        cleaned = cleaned.replace('\x00', '')

        return cleaned.strip()

    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(pattern, email):
            return False

        if len(email) > 254:
            return False

        return True

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        if len(username) < 3 or len(username) > 30:
            return False, "Username must be 3-30 characters"

        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
            return False, "Username must start with a letter"

        return True, "Valid"
