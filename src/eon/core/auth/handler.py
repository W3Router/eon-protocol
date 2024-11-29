```python
from typing import Dict, Any, Optional
import jwt
from datetime import datetime, timedelta
import logging
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class AuthHandler:
    """认证处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.secret = config['jwt_secret']
        self.algorithm = config.get('jwt_algorithm', 'HS256')
        self.access_token_expire_minutes = config.get('access_token_expire_minutes', 30)
        self.security = HTTPBearer()
        self.logger = logging.getLogger(__name__)

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """创建访问令牌"""
        try:
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            self.logger.error(f"Failed to create access token: {str(e)}")
            raise

    def decode_token(self, token: str) -> Dict[str, Any]:
        """解码并验证令牌"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    async def verify_token(self, auth: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> Dict[str, Any]:
        """验证令牌"""
        try:
            return self.decode_token(auth.credentials)
        except Exception as e:
            self.logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )
```