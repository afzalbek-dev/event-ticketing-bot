import hmac
import hashlib
import json
import base64
from typing import Dict, Any, Optional


class TicketSigner:
    """Chiptalarni soxtalashtirishdan himoya qilish uchun HMAC imzoli token yaratish."""

    def __init__(self, secret_key: str):
        if not secret_key:
            raise ValueError("Secret key bo'sh bo'lishi mumkin emas")
        self.secret_key = secret_key.encode("utf-8")

    def generate_token(self, payload: Dict[str, Any]) -> str:
        data_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        payload_b64 = base64.urlsafe_b64encode(data_bytes).decode("utf-8")
        signature = hmac.new(self.secret_key, payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{payload_b64}.{signature}"

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            parts = token.split(".")
            if len(parts) != 2:
                return None
            payload_b64, signature = parts
            expected_sig = hmac.new(self.secret_key, payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected_sig, signature):
                return None
            data_bytes = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
            return json.loads(data_bytes.decode("utf-8"))
        except Exception:
            return None
