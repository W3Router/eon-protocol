```python
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

class AuthHandler:
    """认证处理器"""
    
    def __init__(self):
        self.secret = "your-secret-key"  # 在生产环境中应使用环境变量
        self.algorithm = "HS256"
        self.security = HTTPBearer()
        self.logger = logging.getLogger(__name__)

    def encode_token(self, user_id: str) -> str:
        """生成JWT令牌"""
        payload = {
            'exp': datetime.utcnow() + timedelta(hours=8),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Dict:
        """解析JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token has expired")
            raise HTTPException(status_code=401, detail='Token has expired')
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid token")
            raise HTTPException(status_code=401, detail='Invalid token')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        """认证包装器"""
        return self.decode_token(auth.credentials)
```