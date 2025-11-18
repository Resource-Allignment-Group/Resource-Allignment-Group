import bcrypt


def hash_password(password: str):
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")


def check_password(origional_password: str, hashed_password: str):
    origional_password_bytes = origional_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(origional_password_bytes, hashed_password_bytes)
