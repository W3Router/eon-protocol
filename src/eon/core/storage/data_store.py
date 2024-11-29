```python
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import shutil
import aiofiles
import asyncio
import logging
from datetime import datetime
import hashlib

class DataStore:
    """数据存储管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_path = Path(config.get('storage_path', 'data'))
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    async def store_data(self, data: bytes, 
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """存储数据"""
        try:
            # 生成数据ID
            data_id = self._generate_id(data)
            data_path = self.base_path / f"{data_id}.data"
            meta_path = self.base_path / f"{data_id}.meta"

            # 存储数据
            async with aiofiles.open(data_path, 'wb') as f:
                await f.write(data)

            # 存储元数据
            if metadata:
                metadata['created_at'] = datetime.now().isoformat()
                metadata['size'] = len(data)
                async with aiofiles.open(meta_path, 'w') as f:
                    await f.write(json.dumps(metadata))

            self.logger.info(f"Data stored: {data_id}")
            return data_id

        except Exception as e:
            self.logger.error(f"Failed to store data: {str(e)}")
            raise

    async def retrieve_data(self, data_id: str) -> tuple[bytes, Optional[Dict[str, Any]]]:
        """检索数据"""
        try:
            data_path = self.base_path / f"{data_id}.data"
            meta_path = self.base_path / f"{data_id}.meta"

            # 读取数据
            async with aiofiles.open(data_path, 'rb') as f:
                data = await f.read()

            # 读取元数据
            metadata = None
            if meta_path.exists():
                async with aiofiles.open(meta_path, 'r') as f:
                    content = await f.read()
                    metadata = json.loads(content)

            return data, metadata

        except FileNotFoundError:
            raise ValueError(f"Data not found: {data_id}")
        except Exception as e:
            self.logger.error(f"Failed to retrieve data: {str(e)}")
            raise

    async def delete_data(self, data_id: str):
        """删除数据"""
        try:
            data_path = self.base_path / f"{data_id}.data"
            meta_path = self.base_path / f"{data_id}.meta"

            if data_path.exists():
                data_path.unlink()
            if meta_path.exists():
                meta_path.unlink()

            self.logger.info(f"Data deleted: {data_id}")

        except Exception as e:
            self.logger.error(f"Failed to delete data: {str(e)}")
            raise

    def _generate_id(self, data: bytes) -> str:
        """生成唯一数据ID"""
        return hashlib.sha256(data).hexdigest()[:16]

    async def list_data(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """列出存储的数据"""
        try:
            data_list = []
            for meta_path in self.base_path.glob("*.meta"):
                async with aiofiles.open(meta_path, 'r') as f:
                    content = await f.read()
                    metadata = json.loads(content)
                    data_id = meta_path.stem

                    if self._matches_criteria(metadata, filter_criteria):
                        data_list.append({
                            'id': data_id,
                            **metadata
                        })

            return data_list

        except Exception as e:
            self.logger.error(f"Failed to list data: {str(e)}")
            raise

    def _matches_criteria(self, metadata: Dict[str, Any], 
                         criteria: Optional[Dict[str, Any]]) -> bool:
        """检查元数据是否匹配筛选条件"""
        if not criteria:
            return True

        return all(
            k in metadata and metadata[k] == v
            for k, v in criteria.items()
        )

    async def cleanup(self, max_age_hours: int = 24):
        """清理过期数据"""
        try:
            current_time = datetime.now()
            async for meta_path in aiofiles.os.listdir(self.base_path):
                if meta_path.endswith('.meta'):
                    async with aiofiles.open(self.base_path / meta_path, 'r') as f:
                        metadata = json.loads(await f.read())
                        created_at = datetime.fromisoformat(metadata['created_at'])
                        age = (current_time - created_at).total_seconds() / 3600

                        if age > max_age_hours:
                            data_id = meta_path[:-5]  # Remove .meta extension
                            await self.delete_data(data_id)

        except Exception as e:
            self.logger.error(f"Failed to cleanup data: {str(e)}")
            raise
```