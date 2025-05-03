import pyotp

def generate_totp_secret():
    return pyotp.random_base32()

def verify_totp_token(secret, token):
    totp = pyotp.TOTP(secret)
    return totp.verify(token)
