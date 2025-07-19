from datetime import date
from key_gen import ALLOWED_KEYS  # type: ignore
import rsa  # type: ignore





# ------------------------------
# Custom Exception
# ------------------------------
class RuleViolation(Exception):
    pass

# ------------------------------
# Rule Engine
# ------------------------------
class RuleEngine:
    def __init__(self, blockchain_ref):
        self.blockchain = blockchain_ref

    def enforce_all_rules(self, data_obj, location, add_by, signature):
        """
        Apply all smart contract validations.
        """
        self._check_authorization(add_by)
        self._verify_signature(data_obj, location, add_by, signature)
        self._check_required_fields(data_obj)
        self._check_expiry(data_obj)
        self._check_duplicate_batch(data_obj.batch_id)
        

    # ------------------------------
    # Rule Definitions
    # ------------------------------
    def _check_authorization(self, add_by):
        if add_by not in ALLOWED_KEYS:
            raise RuleViolation(f"{add_by} is not authorized to add blocks.")

    

    def _verify_signature(self, data_obj, location, add_by, signature):
        payload = self._build_payload(data_obj, location, add_by)
        try:
            rsa.verify(payload.encode(), signature, ALLOWED_KEYS[add_by])
        except rsa.VerificationError:
            raise RuleViolation("Invalid digital signature.")

    def _check_required_fields(self, data_obj):
        if not all([data_obj.name, data_obj.manufacturer, data_obj.batch_id]):
            raise RuleViolation("Missing important medicine info.")

    def _check_expiry(self, data_obj):
        if data_obj.expiry_date <= date.today():
            raise RuleViolation("Medicine is expired.")
        

    def _check_duplicate_batch(self, batch_id):
        existing_batch_ids = set(
            block.data.batch_id for block in self.blockchain.get_all_blocks()[1:]
        )
        if batch_id in existing_batch_ids:
            raise RuleViolation("Duplicate batch ID detected.")



    def test_duplicate_batch_rejected(self):
        with self.assertRaises(ValueError):
            payload = f"{self.valid_data.batch_id}|{self.valid_data.name}|{self.valid_data.manufacturer}|{self.valid_data.expiry_date}|{self.user}|{self.location}"
            signature = rsa.sign(payload.encode(), PRIVATE_KEYS[self.user], "SHA-256")
            self.chain.add_block(self.valid_data, self.location, self.user, signature)
    



    # ------------------------------
    # Helpers
    # ------------------------------
    def _build_payload(self, data, location, add_by):
        return f"{data.batch_id}|{data.name}|{data.manufacturer}|{data.expiry_date}|{add_by}|{location}"
