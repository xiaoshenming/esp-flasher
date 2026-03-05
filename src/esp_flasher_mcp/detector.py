"""ESP-IDF 项目自动检测"""
import os
from pathlib import Path
from typing import Optional

class ESPProjectDetector:
    @staticmethod
    def detect(path: Optional[str] = None) -> Optional[dict]:
        """检测 ESP-IDF 项目

        Returns:
            {
                'path': '/path/to/project',
                'name': 'project_name',
                'build_dir': '/path/to/project/build'
            }
        """
        search_path = Path(path) if path else Path.cwd()

        # 向上查找包含 CMakeLists.txt 和 main/ 的目录
        current = search_path.resolve()
        for _ in range(5):  # 最多向上5层
            if (current / "CMakeLists.txt").exists() and (current / "main").is_dir():
                return {
                    'path': str(current),
                    'name': current.name,
                    'build_dir': str(current / "build")
                }
            if current.parent == current:
                break
            current = current.parent

        return None
