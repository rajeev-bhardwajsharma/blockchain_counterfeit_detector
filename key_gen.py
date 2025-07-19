import rsa

stakeholders = ["PharmaCorp","OldLabs","MediLife","pharma1", "pharma2", "pharma3", "pharma4", "pharma5"]

ALLOWED_KEYS={}

PRIVATE_KEYS={}

for name in stakeholders:
    pulic_key ,private_key=rsa.newkeys(512)
    ALLOWED_KEYS[name]=pulic_key
    PRIVATE_KEYS[name]=private_key


