# In blockchain.py

import hashlib
from datetime import date
from block import Block, data
from key_gen import ALLOWED_KEYS, PRIVATE_KEYS # type: ignore
from SecureTransfer import SecureTransfer
from RuleEngine import RuleViolation, RuleEngine # type: ignore
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

GENESIS_DATA = data(batch_id=-1, name="Genesis", manufacturer="System", expiry_date=date.today())

class BlockChain:
    # REFACTORED __init__
    def __init__(self, medicine_data: data, creator_id: str, initial_location: str):
        """
        Initializes a new blockchain.
        This creates the Genesis Block (index 0) and the first real block 
        (index 1) representing the product's creation, signed by the creator.
        """
        if creator_id not in PRIVATE_KEYS:
            raise ValueError(f"Creator '{creator_id}' does not have a private key to sign the first block.")

        # 1. Create the Genesis Block (the anchor of the chain)
        self.head = self._create_genesis_block()
        self.last_block = self.head

        # 2. Create and add the first "Manufacturing" block
        self._create_and_add_first_block(medicine_data, creator_id, initial_location)

        # 3. Initialize the rule engine AFTER the chain has its first real block
        self.rule_engine = RuleEngine(self)


    def _create_genesis_block(self):
        """Creates the static, unchangeable first block of the chain."""
        genesis_hash = hashlib.sha256("GENESIS".encode()).hexdigest()
        return Block(
            index=0,
            data=GENESIS_DATA,
            previous_block=None,
            previous_hash=genesis_hash,
            location="SYSTEM",
            added_by="SYSTEM",
            signature=b"GENESIS",
            status="CREATED",
            current_owner="SYSTEM",
            transfer_history=[]
        )

    # NEW HELPER METHOD
    def _create_and_add_first_block(self, medicine_data: data, creator_id: str, initial_location: str):
        """Creates, signs, and adds the first data-bearing block to the chain."""
        # The payload for the creation event
        payload_to_sign = self.build_payload(medicine_data, initial_location, creator_id).encode('utf-8')

        # The creator signs the payload with their private key
        signature = PRIVATE_KEYS[creator_id].sign(
            payload_to_sign,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Create the first real block
        first_block = Block(
            index=1,
            data=medicine_data,
            previous_block=self.head,
            previous_hash=self.head.hash,
            location=initial_location,
            added_by=creator_id,
            signature=signature, # The signature from the creator
            status="MANUFACTURED",
            current_owner=creator_id, # The creator is the first owner
            transfer_history=[] # History is empty, this is the origin
        )

        # Link this block to the chain
        self.last_block = first_block
        print(f"Blockchain initialized for Batch ID {medicine_data.batch_id}. First block created by {creator_id}.")

    # The rest of your blockchain.py file (build_payload, secure_add_block, etc.) remains the same.
    # Make sure you have made the changes to secure_add_block and the RuleEngine as discussed before.

    def build_payload(self, data, location, add_by):
        return f"{data.batch_id}|{data.name}|{data.manufacturer}|{data.expiry_date}|{add_by}|{location}"


    def secure_add_block(self, buyer: str, new_status: str, new_location: str):
        """
        Complete secure transfer:
        1. Sender signs payload and encrypts block
        2. Buyer decrypts and verifies signature
        3. RuleEngine enforces policies and checks authenticity
        4. New block is added to the chain
        """



        last = self.last_block  # it takes the object of blockchain class which can be viewed as list of block last is the current block or say seller block
        sender = last.current_owner  # get the seller or currennt owner name
        # Verify sender owns the block
        if not last.is_legitimate_owner(sender):
            raise ValueError("Current owner cannot initiate transfer")
        
        # Construct the payload representing this transfer , must match exactly for signing and verifying
        transfer_payload = self.build_payload(last.data, last.location, sender) 

        # Step 1: SecureTransfer initiate encrypted transfer as well as verify
        # The sender signs the payload with their private key. This signature proves authorship.
        encrypted_block, transfer_sig = SecureTransfer.initiate_transfer(
            initiated_by=sender,
            buyer=buyer,
            block=last,
            payload_to_sign=transfer_payload.encode()
        )

        # Step 2: Buyer receives and decrypts it and retrieves sender's signature
        # The original (pre-signed) payload must also be passed for later signature verification
        received_data, location, add_by, sig = SecureTransfer.receive_transfer(
            initiated_by=sender,
            buyer=buyer,
            encrypted_block=encrypted_block,
            new_location=new_location,
            signature=transfer_sig,
            original_payload=transfer_payload.encode()
        )
     
            # Step 3: Enforce smart contract rules and validate sender's digital signature
            # This ensures the sender is authentic and the payload has not been tampered with.

        try:
            self.rule_engine.enforce_all_rules(received_data, new_location, add_by, sig,transfer_payload,sender)
        except RuleViolation as rv:
            print(f" Rule violation: {rv}")
            raise

         #4 . Create new block (using transfer signature)
        new_block = Block(
            index=self.last_block.index + 1,
            data=received_data,
            previous_block=last,
            previous_hash=last.hash,
            location=location,
            added_by=buyer,  # The buyer is adding this new block
            signature=transfer_sig,  # Reuse the transfer signature
            status=new_status,
            current_owner=buyer,
            transfer_history=[*last.transfer_history, sender]
        )
        
        self.last_block = new_block
        print(f"Secure Block Added — Now owned by {buyer} at {new_location}")

    def validate(self):
        current_block = self.last_block

        while current_block is not None:
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_block is not None:
                if current_block.previous_hash != current_block.previous_block.calculate_hash():
                    return False
            current_block = current_block.previous_block

        return True

    def get_all_blocks(self):
        # Go from last block to head (reverse order)
        blocks = []
        current = self.last_block
        while current:
            blocks.insert(0, current)
            current = current.previous_block
        return blocks

    def print_chain(self):
        current = self.last_block
        while current:
            print(f"Index: {current.index}, Location: {current.location}, By: {current.added_by}, Hash: {current.hash}")
            current = current.previous_block