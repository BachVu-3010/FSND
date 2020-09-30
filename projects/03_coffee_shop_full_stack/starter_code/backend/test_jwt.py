import jwt

secret = "secret"

message = {
    "name": "Bach Vu",
    "id": "0123"
}


# HS256 is a symmetric algorithm, meaning there is one secret key shared between AuthRocket and
# the recipient of the token.
# The same key is used to both create the signature and to validate it.

# encoded = jwt.encode(message, secret, "algorithm"="HS256")
encoded_jwt = jwt.encode(message, secret, algorithm="HS256")

print(encoded_jwt)

decoded_jwt = jwt.decode(encoded_jwt, secret, algorithms=["HS256"])

print(decoded_jwt)
