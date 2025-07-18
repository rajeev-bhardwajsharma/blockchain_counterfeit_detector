import hashlib
import time
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class data:
    batch_id: int
    name: str
    manufacturer: str
    expiry_date: date


class Block:
    def __init__(self, index , data ,previous_block, previous_hash , location , add_by , timestamp=None):
        self.index = index
        self.timestamp = timestamp or time.time()
        self.data = data
        self.previous_block = previous_block
        self.location = location
        self.add_by = add_by
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_contents = (
            f"{self.index}{self.location}{self.add_by}"
            f"{self.timestamp}{self.data.batch_id}{self.data.name}"
            f"{self.data.manufacturer}{self.data.expiry_date}{self.previous_hash}"
        )
        return hashlib.sha256(block_contents.encode()).hexdigest()