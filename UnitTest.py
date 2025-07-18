from datetime import date
import unittest
from blockchain import BlockChain
from block import data as Data

class TestBlockchain(unittest.TestCase):
    def setUp(self):
        self.test_data = Data(
            batch_id=15263,
            name="Paracetamol",
            manufacturer="Albeltus",
            expiry_date=date(2026, 8, 5)
        )
        self.chain = BlockChain(self.test_data, "Aligarh", "Albeltus")

    def test_genesis_block(self):
        self.assertEqual(self.chain.head.index, 0)
        self.assertEqual(self.chain.head.data.name, "Paracetamol")
        self.assertEqual(self.chain.head.location, "Aligarh")
        self.assertEqual(self.chain.head.add_by, "Albeltus")

    def test_add_block(self):
        self.chain.add_block("Delhi", "DistributorX")
        self.assertEqual(self.chain.last_block.index, 1)
        self.assertEqual(self.chain.last_block.location, "Delhi")
        self.assertEqual(self.chain.last_block.add_by, "DistributorX")
        self.assertEqual(self.chain.last_block.previous_block, self.chain.head)

    def test_validation(self):
        self.chain.add_block("Delhi", "DistributorX")
        self.chain.add_block("Lucknow", "RetailerY")
        self.assertTrue(self.chain.validate())  # Should pass

        # Tamper with the data
        self.chain.last_block.data = Data(15263, "FakeMedicine", "FakeCorp", date(2026, 8, 5))
        self.assertFalse(self.chain.validate())  # Should fail now

if __name__ == '__main__':
    unittest.main()
