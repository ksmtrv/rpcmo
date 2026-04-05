"""Шифрование резервных копий: PBKDF2-HMAC-SHA256 + AES-256-GCM."""

from __future__ import annotations

import base64
import json
import os
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.errors import ValidationError

PBKDF2_ITERATIONS = 480_000
SALT_LEN = 16
NONCE_LEN = 12
KEY_LEN = 32


def encrypt_backup_payload(plaintext: dict[str, Any], passphrase: str) -> dict[str, Any]:
    raw = json.dumps(plaintext, ensure_ascii=False, default=str).encode("utf-8")
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LEN,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    key = kdf.derive(passphrase.encode("utf-8"))
    aes = AESGCM(key)
    ciphertext = aes.encrypt(nonce, raw, associated_data=None)
    return {
        "fincontrol_encrypted": True,
        "crypto_version": 1,
        "kdf": "pbkdf2-sha256",
        "pbkdf2_iterations": PBKDF2_ITERATIONS,
        "salt_b64": base64.b64encode(salt).decode("ascii"),
        "nonce_b64": base64.b64encode(nonce).decode("ascii"),
        "ciphertext_b64": base64.b64encode(ciphertext).decode("ascii"),
    }


def decrypt_backup_payload(envelope: dict[str, Any], passphrase: str) -> dict[str, Any]:
    if envelope.get("fincontrol_encrypted") is not True:
        raise ValidationError("файл не является зашифрованной резервной копией Fincontrol", {})
    try:
        salt = base64.b64decode(envelope["salt_b64"])
        nonce = base64.b64decode(envelope["nonce_b64"])
        ciphertext = base64.b64decode(envelope["ciphertext_b64"])
    except (KeyError, ValueError, TypeError) as e:
        raise ValidationError("повреждённый формат зашифрованного архива", {}) from e

    iterations = int(envelope.get("pbkdf2_iterations", PBKDF2_ITERATIONS))
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LEN,
        salt=salt,
        iterations=iterations,
    )
    key = kdf.derive(passphrase.encode("utf-8"))
    aes = AESGCM(key)
    try:
        plain = aes.decrypt(nonce, ciphertext, associated_data=None)
    except InvalidTag as e:
        raise ValidationError("неверный пароль или повреждённый ciphertext", {}) from e
    try:
        return json.loads(plain.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise ValidationError("после расшифровки получен некорректный JSON", {}) from e


def resolve_import_body(body: dict[str, Any]) -> dict[str, Any]:
    """
    - Раньше: тело = голый снимок { version, user_id, ... }.
    - Зашифрованный файл: {"passphrase": "…", "backup": { fincontrol_encrypted, … }}.
    - Незашифрованный файл в обёртке: {"backup": { version, user_id, … }}.
    """
    backup = body.get("backup")
    if isinstance(backup, dict):
        phrase = (body.get("passphrase") or "").strip()
        if backup.get("fincontrol_encrypted") is True:
            if not phrase:
                raise ValidationError(
                    "для зашифрованной копии передайте passphrase в JSON вместе с backup",
                    {},
                )
            return decrypt_backup_payload(backup, phrase)
        return backup
    if body.get("fincontrol_encrypted") is True:
        raise ValidationError(
            'оберните файл импорта: {"passphrase":"ваш пароль","backup": <содержимое .json>}',
            {},
        )
    return body
