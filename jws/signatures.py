import json
from authlib.jose import JsonWebSignature
from authlib.jose import JsonWebKey
from jwk import private_pem, public_pem

# 1. Import the public key as JWK
jwk = JsonWebKey.import_key(public_pem)
print(json.dumps(jwk.as_dict(), indent=2))

# 2. Define the payload and JWS header
payload = json.dumps({'user_id': '12345', 'scope': 'read write'}).encode('utf-8')
protected_header = {'alg': 'RS256'}
jws = JsonWebSignature()

# --- Compact Serialization ---
print("## Compact Serialization ##\n")

# 3. Create and verify the compact signature
compact_jws = jws.serialize_compact(protected_header, payload, private_pem)
print(f"Generated Compact JWS:\n{compact_jws}\n")

verified_compact_data = jws.deserialize_compact(compact_jws, public_pem)
print("Compact JWS Verified Successfully!")
print(f"Decoded Payload: {verified_compact_data['payload'].decode('utf-8')}\n")

# --- JSON Serialization (Flattened) ---
print("## JSON Serialization (Flattened) ##\n")

# 4. Create and verify the JSON signature
json_header = {'protected': {'alg': 'RS256'}, 'header': {'kid': 'my-key-id-1'}}
json_jws = jws.serialize_json(json_header, payload, private_pem)
print(f"Generated JSON JWS (Flattened):\n{json.dumps(json_jws, indent=2)}\n")

# Verify the JSON signature
verified_json_data = jws.deserialize_json(json_jws, public_pem)
print("JSON JWS Verified Successfully!")
print(f"Decoded Payload: {verified_json_data['payload'].decode('utf-8')}")