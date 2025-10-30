import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Stakeholders list
stakeholders = ["PharmaCorp", "Dist_X", "Retail_Y", "SYSTEM"]

ALLOWED_KEYS = {}
PRIVATE_KEYS = {}

def generate_keys_for_stakeholders(names):
    """Generates RSA key pairs for all stakeholders."""
    for name in names:
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        PRIVATE_KEYS[name] = private_key
        ALLOWED_KEYS[name] = public_key
    print(f"Generated RSA key pairs for: {', '.join(names)}")


def get_serialized_private_key_pkcs8(name):
    """Serializes private key in PKCS#8 PEM format (for backend)."""
    return PRIVATE_KEYS[name].private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

def get_serialized_public_key(name):
    return ALLOWED_KEYS[name].public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def get_serialized_private_key_pkcs1(name):
    """Serializes private key in PKCS#1 PEM format (for frontend JS)."""
    return PRIVATE_KEYS[name].private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,  # PKCS1
        encryption_algorithm=serialization.NoEncryption()
    )


def save_keys_to_files():
    """Saves private keys in both PKCS8 and PKCS1 formats."""
    os.makedirs("keys", exist_ok=True)
    for name in stakeholders:
        # Save PKCS8 private key
        with open(f"keys/{name}_private_pkcs8.pem", "wb") as f:
            f.write(get_serialized_private_key_pkcs8(name))
        # Save PKCS1 private key
        with open(f"keys/{name}_private_pkcs1.pem", "wb") as f:
            f.write(get_serialized_private_key_pkcs1(name))
        # Save public key
        with open(f"keys/{name}_public.pem", "wb") as f:
            f.write(get_serialized_public_key(name))
    print("Public n Private keys saved in both PKCS#8 and PKCS#1 formats in 'keys' directory.")


if __name__ == '__main__':
    generate_keys_for_stakeholders(stakeholders)
    save_keys_to_files()
