"""AES-GCM encryption helper for media files."""
from pathlib import Path
from typing import TYPE_CHECKING

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

if TYPE_CHECKING:
    from whatsapp_archive.gui.worker import ChatWorker


def encrypt_file(
    input_path: Path,
    output_path: Path,
    key_hex: str,
    worker: "ChatWorker",
) -> None:
    """Encrypt a file with AES-GCM. Writes nonce (16) + tag (16) + ciphertext to output_path."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        key_bytes = bytes.fromhex(key_hex)
        cipher = AES.new(key_bytes, AES.MODE_GCM)

        with open(input_path, "rb") as f:
            file_data = f.read()

        ciphertext, tag = cipher.encrypt_and_digest(file_data)

        with open(output_path, "wb") as f:
            f.write(cipher.nonce)
            f.write(tag)
            f.write(ciphertext)

    except Exception as e:
        logger.exception("Failed to encrypt %s: %s", input_path.name, e)
        worker.status_updated.emit("status_encrypting_error", {"filename": input_path.name})
