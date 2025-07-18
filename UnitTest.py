import unittest
from datetime import date, timedelta
from block import Block, data
from blockchain import BlockChain

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

        self.chain = BlockChain(self.sample_data1, "Mumbai", "PharmaCorp")

    def test_genesis_block_created(self):
        self.assertEqual(self.chain.head.index, 0)
        self.assertEqual(self.chain.head.data.name, "Genesis")

    def test_add_valid_block(self):
        self.chain.add_block(self.sample_data2, "Delhi", "MediLife")
        self.assertEqual(self.chain.last_block.data.batch_id, 102)
        self.assertEqual(self.chain.last_block.location, "Delhi")
        self.assertEqual(self.chain.last_block.add_by, "MediLife")

    def test_duplicate_batch_rejected(self):
        self.chain.add_block(self.sample_data1, "Mumbai", "PharmaCorp") # to explicitly get into duplicate
        with self.assertRaises(ValueError):
            self.chain.add_block(self.duplicate_data, "Bangalore", "FakePharma")

    def test_expired_medicine_rejected(self):
        with self.assertRaises(ValueError):
            self.chain.add_block(self.expired_data, "Chennai", "OldLabs")

    def test_chain_validation(self):
        self.chain.add_block(self.sample_data2, "Delhi", "MediLife")
        self.assertTrue(self.chain.validate())

if __name__ == "__main__":
    unittest.main()
