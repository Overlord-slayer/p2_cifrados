import pyotp

def generate_totp_secret() -> str:
    """
    Genera una nueva clave secreta para TOTP (Time-based One-Time Password).

    Returns:
        str: Una cadena base32 segura que representa el secreto TOTP generado.

    Uso:
        Este secreto debe ser almacenado en la base de datos del usuario
        y usado para generar un código QR que el usuario puede escanear
        con una app como Google Authenticator o Authy.

    Ejemplo:
        >>> secret = generate_totp_secret()
        >>> print(secret)
        'JBSWY3DPEHPK3PXP'

    Seguridad:
        La clave generada es única por usuario y cumple con los estándares de TOTP (RFC 6238).
    """
    return pyotp.random_base32()

def verify_totp_token(secret: str, token: str) -> bool:
    """
    Verifica si un código TOTP proporcionado por el usuario es válido.

    Args:
        secret (str): El secreto base32 del usuario (almacenado durante el registro).
        token (str): El código de 6 dígitos proporcionado por el usuario.

    Returns:
        bool: True si el token es válido dentro de la ventana de tiempo actual, False si no lo es.

    Uso:
        Esta función se llama durante el inicio de sesión para validar que el usuario
        ingresó un código válido desde su app de autenticación.

    Ejemplo:
        >>> verify_totp_token("JBSWY3DPEHPK3PXP", "123456")
        True

    Seguridad:
        La verificación está basada en tiempo, por lo que los códigos expiran cada 30 segundos.
        Internamente, se utiliza `pyotp.TOTP.verify()` con verificación segura contra ataques de repetición.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(token)
