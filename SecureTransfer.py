from datetime import date
from block import data
from key_gen import ALLOWED_KEYS, PRIVATE_KEYS
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import json
import zlib

class SecureTransfer:
    
    MAX_ENCRYPTABLE_SIZE = 214  # For RSA-2048

    @staticmethod
    def _compress_data(data_dict: dict) -> bytes:
        """Compress data to stay within size limits"""
        json_str = json.dumps(data_dict, separators=(',', ':'))  # Most compact JSON
        compressed = zlib.compress(json_str.encode('utf-8'))
        
        if len(compressed) > SecureTransfer.MAX_ENCRYPTABLE_SIZE:
            data_dict.pop('manufacturer', None)
            data_dict.pop('location', None)
            json_str = json.dumps(data_dict, separators=(',', ':'))
            compressed = zlib.compress(json_str.encode('utf-8'))
            
            if len(compressed) > SecureTransfer.MAX_ENCRYPTABLE_SIZE:
                minimal_data = {
                    'batch_id': data_dict['batch_id'],
                    'name': data_dict['name'][:30],
                    'expiry_date': data_dict['expiry_date']
                }
                compressed = zlib.compress(json.dumps(minimal_data).encode('utf-8'))
        
        return compressed

    @staticmethod
    def _serialize_block(block) -> bytes:
        """Safe serialization of block data"""
        data_dict = {
            'batch_id': block.data.batch_id,
            'name': block.data.name,
            'manufacturer': block.data.manufacturer,
            'expiry_date': block.data.expiry_date.isoformat(),
            'index': block.index,
            'owner': block.current_owner
        }
        return SecureTransfer._compress_data(data_dict)
    
    @staticmethod
    def initiate_transfer(initiated_by: str, buyer: str, block,payload_to_sign:bytes) -> tuple[bytes, bytes]:
        """Encrypts the block data for the buyer and signs the payload using sender's private key"""
        """Initiate a secure transfer with  signature"""
        if not block.is_legitimate_owner(initiated_by):
            raise ValueError("Sender lacks ownership rights")

        try:
            block_bytes = SecureTransfer._serialize_block(block)
            if len(block_bytes) > SecureTransfer.MAX_ENCRYPTABLE_SIZE:
                raise ValueError(
                    f"Data too large after compression ({len(block_bytes)} bytes). "
                    f"Maximum allowed: {SecureTransfer.MAX_ENCRYPTABLE_SIZE}"
                )
             # Encrypt block using buyer's/add_by public key  
            encrypted_block = ALLOWED_KEYS[buyer].encrypt(
                block_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Sign the specific transfer payload with sender/seller private key 
            signature = PRIVATE_KEYS[initiated_by].sign(
                payload_to_sign,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            # Return encrypted block (only buyer can decrypt) and sender's digital signature (used to verify authenticity)
            return encrypted_block, signature
            
        except Exception as e:
            raise ValueError(f"Transfer initiation failed: {str(e)}")

    @staticmethod
    def receive_transfer(initiated_by: str, buyer: str, 
                       encrypted_block: bytes, new_location: str, 
                       signature: bytes,original_payload:bytes) -> tuple[data, str, str, bytes]:
        """Transfer receive verifies sender's signature and decrypts the received block data."""
         # Signature must be verified before decrypting the payload
        try:
            
            ALLOWED_KEYS[initiated_by].verify(
                signature,
                original_payload,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except ValueError as e:
            print("The payout is being corrupted")
        
        try:
            # Decrypt with buyer's private key
            decrypted_bytes = PRIVATE_KEYS[buyer].decrypt(
                encrypted_block,
                padding.OAEP(
                    mgf=padding.MGF1(hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        except ValueError as e:
            print("The buyer is not authorised")
            # Handle both compressed and uncompressed data
        try:
            decompressed = zlib.decompress(decrypted_bytes).decode('utf-8')
            data_dict = json.loads(decompressed)
        except zlib.error:
            data_dict = json.loads(decrypted_bytes.decode('utf-8'))
        
        return (
            data(
                batch_id=data_dict['batch_id'],
                name=data_dict.get('name', 'Unknown'),
                manufacturer=data_dict.get('manufacturer', 'Unknown'),
                expiry_date=date.fromisoformat(data_dict['expiry_date'])
            ),
            new_location,
            buyer,
            signature# The sender's digital signature over the original transfer payload.
                    # This proves authenticity (only sender could have signed) and integrity (payload unchanged).
        )