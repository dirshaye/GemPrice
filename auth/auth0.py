from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from jose.exceptions import JWKError
import requests
import os
from typing import Optional
from models import User


security = HTTPBearer()


class Auth0JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(Auth0JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Invalid authentication scheme."
                )
            
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Invalid token or expired token."
                )
            
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Invalid authorization code."
            )

    def verify_jwt(self, token: str) -> bool:
        try:
            payload = self.decode_token(token)
            return payload is not None
        except:
            return False

    def decode_token(self, token: str) -> Optional[dict]:
        try:
            # Get the key from Auth0
            jwks_url = f"https://{os.getenv('AUTH0_DOMAIN')}/.well-known/jwks.json"
            jwks = requests.get(jwks_url).json()
            
            # Get the algorithm from token header
            unverified_header = jwt.get_unverified_header(token)
            
            # Find the correct key
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
                    break
            
            if rsa_key:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=[os.getenv('AUTH0_ALGORITHMS', 'RS256')],
                    audience=os.getenv('AUTH0_AUDIENCE'),
                    issuer=f"https://{os.getenv('AUTH0_DOMAIN')}/"
                )
                return payload
        except JWTError as e:
            print(f"JWT Error: {e}")
            return None
        except JWKError as e:
            print(f"JWK Error: {e}")
            return None
        except Exception as e:
            print(f"General Error: {e}")
            return None
        return None


auth_handler = Auth0JWTBearer()


async def get_current_user(token: str = Depends(auth_handler)) -> User:
    """
    Extract user information from the JWT token
    """
    try:
        payload = auth_handler.decode_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        user = User(
            sub=payload.get("sub"),
            email=payload.get("email"),
            name=payload.get("name")
        )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
