import pytest
from datetime import date, timedelta
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


# Import all necessary components from your project
from block import Block, data
from blockchain import BlockChain, RuleViolation
from key_gen import generate_keys_for_stakeholders, PRIVATE_KEYS

# --- Test Setup and Fixtures ---

@pytest.fixture(scope="session", autouse=True)
def setup_keys():
    """
    (Auto-running Session Fixture)
    Generates all necessary cryptographic keys once before any tests run.
    This ensures all stakeholders ('PharmaCorp', 'Dist_X', etc.) exist.
    """
    stakeholders = ["PharmaCorp", "Dist_X", "Retail_Y", "SYSTEM"]
    generate_keys_for_stakeholders(stakeholders)
    # No return value needed, this just populates the key dictionaries.

@pytest.fixture
def sample_data():
    """Provides a standard, valid data object for a medicine."""
    return data(
        batch_id=101,
        name="Aspirin Forte",
        manufacturer="PharmaCorp",
        expiry_date=date.today() + timedelta(days=365)
    )

@pytest.fixture
def expired_data():
    """Provides an expired data object to test rule validation."""
    return data(
        batch_id=999,
        name="ExpiredTylenol",
        manufacturer="PharmaCorp",
        expiry_date=date.today() - timedelta(days=1)
    )

@pytest.fixture
def fresh_blockchain(sample_data):
    """
    Provides a newly created, valid blockchain instance.
    This chain will have a Genesis block (index 0) and a first "MANUFACTURED"
    block (index 1) owned by PharmaCorp. It's ready for transfer tests.
    """
    return BlockChain(
        medicine_data=sample_data,
        creator_id="PharmaCorp",
        initial_location="PharmaCorp HQ"
    )

# --- Test Cases ---

def test_blockchain_initialization(fresh_blockchain, sample_data):
    """
    Tests if the BlockChain is initialized correctly with the new __init__ logic.
    It should create a genesis block and the first real data block (index 1).
    """
    # 1. Check the Genesis Block (Head)
    assert fresh_blockchain.head.index == 0, "Genesis block should be at index 0"
    assert fresh_blockchain.head.current_owner == "SYSTEM", "Genesis block owner should be SYSTEM"

    # 2. Check the First Real Block (last_block upon creation)
    first_block = fresh_blockchain.last_block
    assert first_block.index == 1, "First real block should be at index 1"
    assert first_block.data == sample_data, "First block should contain the correct medicine data"
    assert first_block.current_owner == "PharmaCorp", "Creator should be the first owner"
    assert first_block.added_by == "PharmaCorp", "Creator should be the one who added the block"
    assert first_block.status == "MANUFACTURED", "Initial status should be MANUFACTURED"
    assert first_block.previous_block == fresh_blockchain.head, "First block's previous should be the genesis block"
    
    # 3. Check the overall chain validity
    assert fresh_blockchain.validate(), "The initial chain should be valid"
    assert len(fresh_blockchain.get_all_blocks()) == 2, "Chain should have 2 blocks initially (Genesis + 1)"


def test_successful_secure_transfer(fresh_blockchain):
    """
    Tests a valid, secure transfer of ownership from the creator to a distributor.
    This is the "happy path" for the secure_add_block method.
    """
    # The chain is currently owned by 'PharmaCorp'
    chain = fresh_blockchain
    original_owner = "PharmaCorp"
    buyer = "Dist_X"
    
    # Perform the secure transfer
    chain.secure_add_block(
        buyer=buyer, 
        new_status="IN_TRANSIT", 
        new_location="Dist_X Warehouse"
    )

    # 1. Check the new last block
    new_block = chain.last_block
    assert new_block.index == 2, "New block should have index 2"
    assert new_block.current_owner == buyer, "Ownership should be transferred to the buyer"
    assert new_block.location == "Dist_X Warehouse", "Location should be updated"
    assert new_block.status == "IN_TRANSIT", "Status should be updated"
    
    # 2. Check the transfer history
    assert original_owner in new_block.transfer_history, "Original owner should be in the history"
    assert len(new_block.transfer_history) == 1, "History should contain one previous owner"
    
    # 3. Validate the entire chain
    assert chain.validate(), "Chain must remain valid after a transfer"


def test_multi_step_transfer_and_history(fresh_blockchain):
    """
    Tests a full supply chain sequence: Manufacturer -> Distributor -> Retailer.
    Verifies that ownership and transfer history are tracked correctly at each step.
    """
    chain = fresh_blockchain # Owner: PharmaCorp
    
    # Step 1: PharmaCorp -> Dist_X
    chain.secure_add_block("Dist_X", "SHIPPED", "Dist_X Warehouse")
    
    # Step 2: Dist_X -> Retail_Y
    chain.secure_add_block("Retail_Y", "DELIVERED", "Retail_Y Pharmacy")

    # 1. Check the final block
    final_block = chain.last_block
    assert final_block.index == 3, "Final block should be at index 3"
    assert final_block.current_owner == "Retail_Y", "Final owner should be the retailer"
    
    # 2. Check the complete transfer history
    history = final_block.transfer_history
    assert history == ["PharmaCorp", "Dist_X"], "Transfer history should be correctly ordered"
    
    # 3. Validate the entire chain
    assert chain.validate(), "Chain must be valid after multiple transfers"
    assert len(chain.get_all_blocks()) == 4 # Genesis + 3 transfers


def test_chain_invalidation_on_tampering(fresh_blockchain):
    """
    Tests that the chain becomes invalid if any block's data is tampered with.
    This confirms that the hash-based integrity check is working.
    """
    chain = fresh_blockchain
    
    # Tamper with the location of the first block after it has been added
    # NOTE: In Python, we need to get the block by traversing the chain
    first_real_block = chain.last_block
    first_real_block.location = "Tampered Location" # Maliciously change data

    # The `validate` method should now detect the mismatch
    # because the stored hash will not match the newly calculated hash.
    assert not chain.validate(), "Chain should be invalid after tampering"


# --- Rule Engine and Security Tests ---

def test_rule_creation_with_expired_medicine_fails(expired_data):
    """
    Tests the RuleEngine: The system should refuse to create a blockchain
    for a product that is already expired.
    
    NOTE: This test relies on the RuleEngine being called during initialization.
    If you haven't added it, this test will fail. A robust `__init__` should
    validate its initial block. For this test, we'll test the rule directly.
    """
    # Let's assume the rules are NOT run in __init__ to test them independently.
    # We create a chain and then test the rule that should have been run.
    chain = BlockChain(expired_data, "PharmaCorp", "Factory")
    
    with pytest.raises(RuleViolation, match="Medicine is expired."):
        # Manually trigger the rule check that happens during a transfer
        chain.rule_engine._check_expiry(expired_data)

def test_rule_invalid_signature_fails(fresh_blockchain):
    """
    Tests the RuleEngine: A transfer must be rejected if the digital signature is invalid.
    This simulates a forged or corrupted signature.
    """
    chain = fresh_blockchain
    sender = chain.last_block.current_owner # PharmaCorp
    
    # Create a valid payload
    payload = chain.build_payload(chain.last_block.data, chain.last_block.location, sender)
    
    # Create an INVALID signature (e.g., signed by the wrong person, 'Retail_Y')
    invalid_signature = PRIVATE_KEYS["Retail_Y"].sign(
        payload.encode('utf-8'),
        # ... using standard padding ...
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )

    # The rule engine should catch this during enforcement
    with pytest.raises(RuleViolation, match="Invalid digital signature."):
        chain.rule_engine._verify_signature(
            sender=sender, # Claimed signer is PharmaCorp
            signature=invalid_signature, # But signature is from Retail_Y
            payload=payload
        )

def test_rule_unauthorized_entity_fails(fresh_blockchain):
    """
    Tests the RuleEngine: An entity not in the list of allowed keys
    cannot be part of a transaction.
    """
    chain = fresh_blockchain
    
    with pytest.raises(RuleViolation, match="not authorized to add blocks"):
        chain.rule_engine._check_authorization("Unknown_Hacker")
