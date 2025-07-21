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
    def __init__(
        self, 
        index: int,
        data: data,                      # Frozen medicine metadata
        previous_block: 'Block',         # Previous block in chain
        previous_hash: str,              # Hash of previous block
        location: str,                   # Physical location (e.g., "Pharmacy A")
        added_by: str,                   # Who added this block (e.g., "Distributor_X")
        signature: bytes,                # Digital signature from current_owner
        status: str,                     # e.g., "MANUFACTURED", "DELIVERED"
        current_owner: str,              # Public key of owner (e.g., "PharmaCorp_PubKey")
        transfer_history: list[str],     # List of past owners ["Owner1", "Owner2"]
        timestamp: float = None          # Auto-generated if None
    ):
        self.index = index               #what index is it 
        self.timestamp = timestamp or time.time()
        self.data = data                  # Immutable medicine data
        self.previous_block = previous_block
        self.previous_hash = previous_hash
        self.location = location
        self.added_by = added_by
        self.signature = signature
        self.status = status              # New: Track lifecycle state
        self.current_owner = current_owner # New: Ownership tracking
        self.transfer_history = transfer_history.copy()  # New: Audit trail
        self.hash = self.calculate_hash()  # Includes all fields

    #to check that owner that is pretending is real owner or not 
    def is_legitimate_owner(self, claimed_owner: str, require_current: bool = True) -> bool:
            # If this is the genesis block, it's the source of truth — allow whoever was set
        if self.index == 0:
            return True
        #  Check if owner exists in transfer history
        # Only enforce transfer history check if there's a history to validate against
        #if self.transfer_history and claimed_owner not in self.transfer_history:
        
        
        #  If checking current ownership anti-clone verification
        if require_current:
            if claimed_owner != self.current_owner:
                raise ValueError(
                    f"Ownership mismatch: Claimed {claimed_owner} "
                    f"but current owner is {self.current_owner}"
                )
        
        #  Patch work
        if not self.previous_block and claimed_owner != self.added_by:
            raise ValueError("Genesis block owner must match creator")
        
        return True
  
    def calculate_hash(self):
        block_contents = (
            f"{self.index}{self.location}{self.added_by}"
            f"{self.timestamp}{self.data.batch_id}{self.data.name}"
            f"{self.data.manufacturer}{self.data.expiry_date}{self.previous_hash}{self.transfer_history}{self.current_owner}{self.status}"
        )
        return hashlib.sha256(block_contents.encode()).hexdigest()
    #only for nice output
    def __repr__(self):
       return f"<Block {self.index} | Owner: {self.current_owner} | Added By: {self.added_by} | Loc: {self.location}>"
