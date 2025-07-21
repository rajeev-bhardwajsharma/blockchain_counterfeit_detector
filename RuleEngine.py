from datetime import date
from key_gen import ALLOWED_KEYS  # type: ignore #contain public key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


# Custom Exception

class RuleViolation(Exception):
    pass

class RuleEngine:
    def __init__(self, blockchain_ref):
        self.blockchain = blockchain_ref

    def enforce_all_rules(self, data_obj, location, add_by, signature,payload,sender):
        

        #Apply all smart contract validations.

        self._check_authorization(add_by)
        self._verify_signature( signature,payload,sender)
        self._check_required_fields(data_obj)
        self._check_expiry(data_obj)
        #self._check_duplicate_batch(data_obj.batch_id) for future expansion 
        

  
    def _check_authorization(self, add_by):
        #checking if add_by which is infact buyer is even allow to buy or not
        if add_by not in ALLOWED_KEYS:
            raise RuleViolation(f"{add_by} is not authorized to add blocks(buy medicine).")

    

    def _verify_signature(self,signature,payload,sender):
        # Signature verification step:
       # This confirms that the payload was signed by the actual sender using their private key.
       #Note add_by is buyer and sender is current owner seller 
       # This must match the public key of the entity initiating the transfer.
        public_key = ALLOWED_KEYS[sender] 
        try:
            public_key.verify(
                signature,
                payload.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except Exception:
            raise RuleViolation("Invalid digital signature.")

    def _check_required_fields(self, data_obj):
        if not all([data_obj.name, data_obj.manufacturer, data_obj.batch_id]):
            raise RuleViolation("Missing important medicine info.")

    def _check_expiry(self, data_obj):
        if data_obj.expiry_date <= date.today():
            raise RuleViolation("Medicine is expired.")
        


    
