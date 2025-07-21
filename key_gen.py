from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import os


# Define the stakeholders
stakeholders = [
    "PharmaCorp", "OldLabs", "MediLife",
    "Dist_X", "Retail_Y" ,"PharmaCorp", "Dist_X", "Retail_Y", 
    "PharmaX", "SYSTEM"
]

# Create dictionaries to hold keys
ALLOWED_KEYS = {}   # public keys for signature verification
PRIVATE_KEYS = {}   # private keys for signing


def generate_keys_for_stakeholders(names):
    for name in names:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # Save keys in PEM format (you can directly store the objects too, but PEM makes it serializable)
        PRIVATE_KEYS[name] = private_key
        ALLOWED_KEYS[name] = public_key

# Optional: Function to serialize public key if needed
def get_serialized_public_key(name):
    if name not in ALLOWED_KEYS:
        raise ValueError("No such stakeholder")
    return ALLOWED_KEYS[name].public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

# Optional: Function to serialize private key if needed
def get_serialized_private_key(name):
    if name not in PRIVATE_KEYS:
        raise ValueError("No such stakeholder")
    return PRIVATE_KEYS[name].private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

def save_keys_to_files():
    os.makedirs("keys/public", exist_ok=True)
    os.makedirs("keys/private", exist_ok=True)
    for name in stakeholders:
        with open(f"keys/private/{name}_private.pem", "wb") as f:
            f.write(get_serialized_private_key(name))

        with open(f"keys/public/{name}_public.pem", "wb") as f:
            f.write(get_serialized_public_key(name))


if __name__ == '__main__':
    generate_keys_for_stakeholders(stakeholders)
    save_keys_to_files()
