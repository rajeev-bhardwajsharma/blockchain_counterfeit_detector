import datetime
import unittest
from datetime import date, timedelta
from block import data 
from blockchain import BlockChain
from key_gen import PRIVATE_KEYS,ALLOWED_KEYS
import rsa
from RuleEngine import RuleViolation

class TestBlockChain(unittest.TestCase):
    def setUp(self):
        self.user = "PharmaCorp"
        self.location = "Delhi"
        self.valid_data = data(
            batch_id=1,
            name="Paracetamol",
            manufacturer="Pharma Inc.",
            expiry_date=date.today() + timedelta(days=365)
        )
        # Create keypair for testing
        (self.pubkey, self.privkey) = rsa.newkeys(512)
        ALLOWED_KEYS[self.user] = self.pubkey  # overwrite with test key
        PRIVATE_KEYS[self.user]=self.privkey
        payload = f"{self.valid_data.batch_id}|{self.valid_data.name}|{self.valid_data.manufacturer}|{self.valid_data.expiry_date}|{self.user}|{self.location}"
        self.signature = rsa.sign(payload.encode(), PRIVATE_KEYS[self.user], "SHA-256")
        self.chain = BlockChain(self.valid_data, self.location, self.user, self.signature)

    def _generate_signature(self, data_obj):
        payload = self.chain.build_payload(data_obj, self.location, self.user)
        return rsa.sign(payload.encode(), self.privkey, "SHA-256")


    def test_add_valid_block(self):
        new_data = data(
            batch_id=2,
            name="Ibuprofen",
            manufacturer="OldLabs",
            expiry_date=date.today() + timedelta(days=400)
        )
        payload = f"{new_data.batch_id}|{new_data.name}|{new_data.manufacturer}|{new_data.expiry_date}|{self.user}|{self.location}"
        signature = rsa.sign(payload.encode(), PRIVATE_KEYS[self.user], "SHA-256")
        self.chain.add_block(new_data, self.location, self.user, signature)
        self.assertEqual(len(self.chain.get_all_blocks()), 2)

    def test_invalid_signature_raises(self):
        invalid_signature = b"fake_signature"
        new_data = data(
            batch_id=3,
            name="Vitamin C",
            manufacturer="FakePharma",
            expiry_date=date.today() + timedelta(days=100)
        )
        with self.assertRaises(ValueError):
            self.chain.add_block(new_data, self.location, self.user, invalid_signature)

    def test_expired_medicine_rejected(self):
        expired_data = data(
            batch_id="expiredbatch001",
            name="XYZ",
            manufacturer="ExpiredPharma",
            expiry_date=date(2023, 1, 1)
        )
        signature = self._generate_signature(expired_data)
    
        # Catch RuleViolation instead of letting it crash
        with self.assertRaises(RuleViolation):
            self.chain.add_block(expired_data, self.location, self.user, signature)
    
        self.assertEqual(len(self.chain.get_all_blocks()), 1)  # genesis only


    def test_duplicate_batch_rejected(self):
        signature = self._generate_signature(self.valid_data)
        
        # First addition (valid)
        self.chain.add_block(self.valid_data, self.location, self.user, signature)
    
        # Second addition (should raise)
        with self.assertRaises(RuleViolation):
            self.chain.add_block(self.valid_data, self.location, self.user, signature)
    
        self.assertEqual(len(self.chain.get_all_blocks()), 2)  # genesis + 1



    def test_unauthorized_user(self):
        fake_user = "BadActor"
        bad_data = data(
            batch_id=5,
            name="UnknownDrug",
            manufacturer="ShadyCorp",
            expiry_date=date.today() + timedelta(days=100)
        )
        payload = f"{bad_data.batch_id}|{bad_data.name}|{bad_data.manufacturer}|{bad_data.expiry_date}|{fake_user}|{self.location}"
        (_, bad_private_key) = rsa.newkeys(512)
        signature = rsa.sign(payload.encode(), bad_private_key, "SHA-256")
        with self.assertRaises(ValueError):
            self.chain.add_block(bad_data, self.location, fake_user, signature)

if __name__ == '__main__':
    unittest.main()
