import base64
import json

def get_user_id_from_jwt(jwt_token):
    try:
        # Split the token to get the payload part (YY)
        payload_part = jwt_token.split('.')[1]
        
        # Decode the payload from Base64
        payload_decoded = base64.urlsafe_b64decode(payload_part + '==').decode('utf-8')
        user_id = json.loads(payload_decoded)['user_id']
        # Return the last 30 characters of the decoded payload
        return user_id
    except (IndexError, ValueError, base64.binascii.Error) as e:
        print(f"Error decoding JWT payload: {e}")