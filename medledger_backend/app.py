# In app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
import logging
import database # Import our updated database module

app = Flask(__name__)
CORS(app)
database.init_db() # Ensure the database and tables are ready

# --- Key Loading ---
STAKEHOLDERS_PUBLIC_KEYS = {}
def load_public_key_from_pem(path):
    with open(path, 'rb') as f:
        return load_pem_public_key(f.read())

for stakeholder in ["PharmaCorp", "Dist_X", "Retail_Y", "SYSTEM"]:
    try:
        STAKEHOLDERS_PUBLIC_KEYS[stakeholder] = load_public_key_from_pem(f'keys/{stakeholder}_public.pem')
        app.logger.info(f'Loaded public key for {stakeholder}')
    except Exception as e:
        app.logger.error(f'Error loading key for {stakeholder}: {e}')

# --- Signature Verification Helper ---
def verify_signature(public_key, data_str, signature_b64):
    from base64 import b64decode
    try:
        public_key.verify(
            b64decode(signature_b64),
            data_str.encode('utf-8'),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return True, None
    except InvalidSignature:
        return False, "Signature mismatch."
    except Exception as ex:
        return False, f"Verification error: {ex}"

# --- API Endpoints ---

@app.route('/create', methods=['POST'])
def create_batch():
    req_data = request.get_json()
    try:
        batch_id = req_data['batch_id']
        creator_id = req_data['creator_id']
        signature = req_data['signature']
        location = req_data.get('location', 'Manufacturer Warehouse')
        
        # This payload must exactly match the one created on the frontend
        payload = f"{batch_id}|{req_data['name']}|{req_data['manufacturer']}|{req_data['expiry_date']}|{creator_id}|{location}"

        if creator_id not in STAKEHOLDERS_PUBLIC_KEYS:
            return jsonify({'error': f"Unknown creator: {creator_id}"}), 400

        valid, error = verify_signature(STAKEHOLDERS_PUBLIC_KEYS[creator_id], payload, signature)
        if not valid:
            return jsonify({'error': f"Invalid signature: {error}"}), 403

        # Log the creation of this new batch in our state database
        database.log_creation(batch_id, creator_id, location)

        return jsonify({'message': f'Batch {batch_id} successfully created and registered to {creator_id}.'}), 201

    except Exception as e:
        app.logger.error(f"Error in /create: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/transfer', methods=['POST'])
def transfer_batch():
    req_data = request.get_json()
    try:
        batch_id = req_data['batch_id']
        current_owner = req_data['current_owner'] # The one signing the transfer (seller)
        new_owner = req_data['new_owner']         # The recipient (buyer)
        new_location = req_data['new_location']
        signature = req_data['signature']

        # 1. Ownership Check: Verify the sender is the legitimate owner
        state = database.get_current_state(batch_id)
        if not state:
            return jsonify({'error': f'Batch ID {batch_id} not found.'}), 404
        if state['current_owner'] != current_owner:
            return jsonify({'error': f"Ownership conflict: {current_owner} is not the owner of batch {batch_id}."}), 403

        # 2. Signature Check: Verify the signature is valid
        payload = f"{batch_id}|{new_owner}|{new_location}"
        
        if current_owner not in STAKEHOLDERS_PUBLIC_KEYS:
            return jsonify({'error': f"Unknown owner: {current_owner}"}), 400

        valid, error = verify_signature(STAKEHOLDERS_PUBLIC_KEYS[current_owner], payload, signature)
        if not valid:
            return jsonify({'error': f"Invalid signature: {error}"}), 403

        # 3. If all checks pass, update the database
        database.update_owner(batch_id, new_owner, new_location)

        return jsonify({'message': f'Batch {batch_id} successfully transferred to {new_owner}.'}), 200

    except Exception as e:
        app.logger.error(f"Error in /transfer: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/update_status', methods=['POST'])
def update_status():
    req_data = request.get_json()
    try:
        batch_id = req_data['batch_id']
        owner = req_data['owner'] # The one signing the status change
        new_status = req_data['new_status']
        signature = req_data['signature']

        # 1. Ownership Check: Verify the sender is the legitimate owner
        state = database.get_current_state(batch_id)
        if not state:
            return jsonify({'error': f'Batch ID {batch_id} not found.'}), 404
        if state['current_owner'] != owner:
            return jsonify({'error': f"Ownership conflict: {owner} is not the owner of batch {batch_id}."}), 403

        # 2. Signature Check: Verify the signature is valid
        payload = f"{batch_id}|{new_status}"
        
        if owner not in STAKEHOLDERS_PUBLIC_KEYS:
            return jsonify({'error': f"Unknown owner: {owner}"}), 400

        valid, error = verify_signature(STAKEHOLDERS_PUBLIC_KEYS[owner], payload, signature)
        if not valid:
            return jsonify({'error': f"Invalid signature: {error}"}), 403

        # 3. If all checks pass, update the database
        database.update_status(batch_id, new_status)

        return jsonify({'message': f'Status of batch {batch_id} successfully updated to {new_status}.'}), 200

    except Exception as e:
        app.logger.error(f"Error in /update_status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/validate_medicine/<int:batch_id>', methods=['GET'])
def validate_medicine(batch_id):
    """A public endpoint to check the status of a medicine batch."""
    try:
        state = database.get_current_state(batch_id)
        if not state:
            return jsonify({'error': f'Batch ID {batch_id} not found.'}), 404
        
        # Convert the database row to a standard dictionary for the JSON response
        return jsonify(dict(state)), 200

    except Exception as e:
        app.logger.error(f"Error in /validate_medicine: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)