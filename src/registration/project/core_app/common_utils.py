import secrets, string

def generate_random_string(length):
    alphanumeric_characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(alphanumeric_characters) for _ in range(length))
    return random_string