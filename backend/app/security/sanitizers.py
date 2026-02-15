"""
Backend Security - Input Sanitizers
Prevención de: SQL injection, XSS, Path traversal, etc
Uso: sanitize_string(user_input), escape_sql(query), etc
"""

import html
from typing import Any, Dict
from sqlalchemy import text
import re


class SQLSanitizer:
    """Sanitizadores para prevenir SQL injection"""

    @staticmethod
    def parameterized_query(query: str, params: Dict[str, Any]) -> tuple:
        """
        Usar SIEMPRE queries parametrizadas
        ❌ NUNCA: f"SELECT * FROM users WHERE id = {user_id}"
        ✅ CORRECTO: "SELECT * FROM users WHERE id = :user_id", {"user_id": user_id}
        """
        return text(query), params

    @staticmethod
    def escape_like(value: str) -> str:
        """Escapar para LIKE queries"""
        return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

    @staticmethod
    def validate_column_name(column: str, allowed: list[str]) -> str:
        """Whitelist de nombres de columnas (importante para ORDER BY)"""
        if column not in allowed:
            raise ValueError(f"Invalid column: {column}")
        return column

    @staticmethod
    def validate_table_name(table: str, allowed: list[str]) -> str:
        """Whitelist de nombres de tablas"""
        if table not in allowed:
            raise ValueError(f"Invalid table: {table}")
        return table


class XSSSanitizer:
    """Sanitizadores para prevenir XSS"""

    @staticmethod
    def sanitize_html(dirty: str) -> str:
        """Escapar HTML entities"""
        return html.escape(dirty)

    @staticmethod
    def sanitize_url(url: str) -> str:
        """Sanitizar URLs - solo http/https"""
        if not url.startswith(('http://', 'https://')):
            return ''
        return url

    @staticmethod
    def sanitize_json_key(key: str) -> str:
        """Sanitizar keys en JSON responses"""
        # Remover caracteres potencialmente peligrosos
        return re.sub(r'[^\w\-.]', '', key)


class PathTraversalSanitizer:
    """Prevención de path traversal attacks"""

    @staticmethod
    def safe_filename(filename: str) -> str:
        """
        Sanitizar nombres de archivo
        ❌ NO PERMITIR: ../../../etc/passwd, .htaccess, etc
        """
        # Remover path separators
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')

        # Whitelist de caracteres permitidos
        filename = re.sub(r'[^\w\-.]', '', filename)

        # Longitud máxima
        filename = filename[:255]

        if not filename:
            raise ValueError("Invalid filename")

        return filename

    @staticmethod
    def safe_directory_path(base_dir: str, requested_path: str) -> str:
        """
        Asegurar que path no sale de base_dir
        """
        import os
        base = os.path.abspath(base_dir)
        full = os.path.abspath(os.path.join(base, requested_path))

        if not full.startswith(base):
            raise ValueError("Path traversal attempt detected")

        return full


class GeneralSanitizer:
    """Sanitizadores generales"""

    @staticmethod
    def sanitize_string(value: str, max_length: int = 10000) -> str:
        """Sanitizar string general"""
        if not isinstance(value, str):
            return ""

        # Truncar si es muy largo
        value = value[:max_length]

        # Remover null bytes y control characters (excepto whitespace válido)
        value = ''.join(c for c in value if ord(c) >= 32 or c in '\n\t\r')

        return value.strip()

    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitizar diccionario recursivamente"""
        sanitized = {}

        for key, value in data.items():
            # Sanitizar key
            safe_key = re.sub(r'[^\w\-.]', '', str(key))

            # Sanitizar value según tipo
            if isinstance(value, str):
                sanitized[safe_key] = GeneralSanitizer.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[safe_key] = GeneralSanitizer.sanitize_dict(value)
            elif isinstance(value, (int, float, bool)):
                sanitized[safe_key] = value
            elif value is None:
                sanitized[safe_key] = None
            # TODO: Manejar listas

        return sanitized

    @staticmethod
    def remove_null_bytes(value: str) -> str:
        """Remover null bytes"""
        return value.replace('\x00', '')

    @staticmethod
    def normalize_unicode(value: str) -> str:
        """Normalizar Unicode para prevenir homograph attacks"""
        import unicodedata
        return unicodedata.normalize('NFKC', value)
