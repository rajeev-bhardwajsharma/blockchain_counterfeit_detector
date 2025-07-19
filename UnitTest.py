import unittest
from datetime import date, timedelta
from block import Block, data
from blockchain import BlockChain
from dataclasses import FrozenInstanceError

from key_gen import ALLOWED_KEYS,PRIVATE_KEYS
import rsa

class TestBlockChain(unittest.TestCase):

    def setUp(self):
        # Create valid sample data
        self.sample_data1 = data(
            batch_id=101,
            name="Paracetamol",
            manufacturer="PharmaCorp",
            expiry_date=date.today() + timedelta(days=365)
        )
        self.sample_data2 = data(
            batch_id=102,
            name="Ibuprofen",
            manufacturer="MediLife",
            expiry_date=date.today() + timedelta(days=180)
        )
        self.duplicate_data = data(  # same batch ID as sample_data1
            batch_id=101,
            name="Paracetamol",
            manufacturer="FakePharma",
            expiry_date=date.today() + timedelta(days=200)
        )
        self.expired_data = data(
            batch_id=103,
            name="ExpiredMed",
            manufacturer="OldLabs",
            expiry_date=date.today() - timedelta(days=10)
        )

        # Construct a payload if needed
        self.payload =self.build_payload(self.sample_data1,"Mumbai","PharmaCorp")
        self.signature = rsa.sign(self.payload.encode(), PRIVATE_KEYS["PharmaCorp"], 'SHA-256')
        # Create initial blockchain with valid data
        self.chain = BlockChain(self.sample_data1, "Mumbai", "PharmaCorp",self.signature)

        #payload = f"{data.batch_id}|{data.name}|{data.manufacturer}|{data.expiry}|{location}|{add_by}"
        #self.chain = BlockChain(self.sample_data1, "Mumbai", "PharmaCorp")
    
    def build_payload(self,data, location, add_by):
        return f"{data.batch_id}|{data.name}|{data.manufacturer}|{data.expiry_date}|{add_by}|{location}"

    def test_genesis_block_created(self):
        self.assertEqual(self.chain.head.index, 0)
        self.assertEqual(self.chain.head.data.name, "Genesis")

    def test_add_valid_block(self):
        self.chain.add_block(self.sample_data1, "Mumbai", "PharmaCorp",self.signature)
        self.assertEqual(self.chain.last_block.data.batch_id, 101)
        self.assertEqual(self.chain.last_block.location, "Mumbai")
        self.assertEqual(self.chain.last_block.add_by, "PharmaCorp")

    def test_duplicate_batch_rejected(self):
        self.chain.add_block(self.sample_data1, "Mumbai", "PharmaCorp",self.signature) # to explicitly get into duplicate
        #payload = self.build_payload(self.duplicate_data, "Bangalore", "FakePharma")
        fake_signature = b"INVALID_SIGNATURE"
        
        with self.assertRaises(ValueError):
            self.chain.add_block(self.duplicate_data, "Bangalore", "FakePharma", fake_signature)


    def test_expired_medicine_rejected(self):
        payload = self.build_payload(self.expired_data, "Chennai", "OldLabs")
        signature = rsa.sign(payload.encode(), PRIVATE_KEYS["OldLabs"],'SHA-256')
        
        with self.assertRaises(ValueError):
            self.chain.add_block(self.expired_data, "Chennai", "OldLabs", signature)
        

    def test_chain_validation(self):
        payload = self.build_payload(self.sample_data2, "Delhi", "MediLife")
        signature = rsa.sign(payload.encode(), PRIVATE_KEYS["MediLife"],'SHA-256')
        self.chain.add_block(self.sample_data2, "Delhi", "MediLife", signature)
        self.assertTrue(self.chain.validate())

    def test_invalid_signature_rejected(self):
        payload = self.build_payload(self.sample_data2, "Delhi", "MediLife")
        wrong_signature = rsa.sign(payload.encode(), PRIVATE_KEYS["PharmaCorp"], 'SHA-256')  # Signed by wrong person
        with self.assertRaises(ValueError):
            self.chain.add_block(self.sample_data2, "Delhi", "MediLife", wrong_signature)


    def test_unknown_sender_rejected(self):
        unknown_sender = "RandomHacker"
        payload = self.build_payload(self.sample_data2, "Delhi", unknown_sender)
        # generate new private/public key pair not in ALLOWED_KEYS
        pubkey, privkey = rsa.newkeys(512)
        signature = rsa.sign(payload.encode(), privkey, 'SHA-256')
    
        with self.assertRaises(ValueError):
            self.chain.add_block(self.sample_data2, "Delhi", unknown_sender, signature)


    def test_chain_breaks_on_tamper(self):
        payload = self.build_payload(self.sample_data2, "Delhi", "MediLife")
        signature = rsa.sign(payload.encode(), PRIVATE_KEYS["MediLife"], 'SHA-256')
        self.chain.add_block(self.sample_data2, "Delhi", "MediLife", signature)
    
        blocks = self.chain.get_all_blocks()
        with self.assertRaises(FrozenInstanceError):
            blocks[1].data.name = "TamperedDrug"

    
        self.assertFalse(self.chain.validate())

    def test_timestamp_exists(self):
        payload = self.build_payload(self.sample_data2, "Goa", "MediLife")
        signature = rsa.sign(payload.encode(), PRIVATE_KEYS["MediLife"], 'SHA-256')
        self.chain.add_block(self.sample_data2, "Goa", "MediLife", signature)
    
        self.assertIsNotNone(self.chain.last_block.timestamp)


    def test_multiple_blocks_added(self):
       payload = self.build_payload(self.sample_data2, "Delhi", "MediLife")
       signature = rsa.sign(payload.encode(), PRIVATE_KEYS["MediLife"], 'SHA-256')
       self.chain.add_block(self.sample_data2, "Delhi", "MediLife", signature)
   
       blocks = self.chain.get_all_blocks()
   
       self.assertEqual(blocks[1].data.name, "Ibuprofen")  # genesis is at 0
       self.assertEqual(blocks[2].data.name, "Paracetamol")





if __name__ == "__main__":
    unittest.main()
