"""
Backend Security - Encryption for PII (Personally Identifiable Information)
Uso: encrypt_pii(ssn), decrypt_pii(encrypted_ssn), hash_password(pwd), verify_password(pwd, hash)
"""

import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import bcrypt
import base64


class EncryptionService:
    """Servicio de encriptación para datos sensibles"""

    def __init__(self):
        # Obtener clave de encriptación desde variable de entorno
        key_env = os.getenv('ENCRYPTION_KEY')
        if not key_env:
            raise ValueError("ENCRYPTION_KEY not set in environment")

        self.cipher = Fernet(key_env.encode() if isinstance(key_env, str) else key_env)

    @staticmethod
    def generate_encryption_key() -> str:
        """
        Generar clave de encriptación nueva
        ⚠️ Guardar en .env de forma segura
        """
        return Fernet.generate_key().decode()

    def encrypt_pii(self, value: str) -> str:
        """
        Encriptar dato sensible (PII)
        - SSN
        - Números de tarjeta de crédito
        - Información de salud
        """
        if not value:
            return ""

        encrypted = self.cipher.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_pii(self, encrypted_value: str) -> str:
        """Desencriptar dato sensible"""
        if not encrypted_value:
            return ""

        try:
            decoded = base64.b64decode(encrypted_value)
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")


class PasswordService:
    """Servicio de contraseñas seguras"""

    # Configuración bcrypt
    BCRYPT_ROUNDS = 12  # 10-12 es estándar (más alto = más lento pero más seguro)

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash de contraseña con bcrypt + salt aleatorio
        ✅ NUNCA guardar contraseña en plain text
        ✅ SIEMPRE usar bcrypt (o argon2)
        """
        salt = bcrypt.gensalt(rounds=PasswordService.BCRYPT_ROUNDS)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verificar contraseña contra hash
        Retorna True si coinciden
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            print(f"Password verification error: {e}")
            return False

    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generar token seguro (para reset password, etc)"""
        return base64.b64encode(os.urandom(length)).decode()


class KeyDerivationService:
    """Derivación de claves usando PBKDF2"""

    @staticmethod
    def derive_key(password: str, salt: bytes, length: int = 32) -> bytes:
        """Derivar clave segura de contraseña"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            iterations=100000,  # NIST recomienda 600000+
            backend=default_backend(),
        )
        return kdf.derive(password.encode())


# Singleton instances
try:
    encryption_service = EncryptionService()
except ValueError:
    encryption_service = None  # No se pudo inicializar

password_service = PasswordService()
