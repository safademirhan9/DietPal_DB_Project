from flask_security.utils import _security, get_hmac, _pwd_context


def verify_password(password, password_hash):
    """Returns ``True`` if the password matches the supplied hash.

    :param password: A plaintext password to verify
    :param password_hash: The expected hash value of the password (usually form your database)
    """
    if _security.password_hash != 'plaintext':
        password = get_hmac(password)

    return _pwd_context.verify(password, password_hash)