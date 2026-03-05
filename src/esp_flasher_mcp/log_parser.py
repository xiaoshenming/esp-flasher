"""日志解析器 - 提取编译/烧录/监控关键信息"""
import re
from typing import Dict, List, Optional

class LogParser:
    @staticmethod
    def parse_build_progress(line: str) -> Optional[Dict]:
        """解析编译进度: [67/120] Building..."""
        match = re.search(r'\[(\d+)/(\d+)\]', line)
        if match:
            current, total = int(match.group(1)), int(match.group(2))
            return {
                'stage': 'building',
                'current': current,
                'total': total,
                'percentage': int(current / total * 100),
                'message': line.strip()
            }
        return None

    @staticmethod
    def parse_flash_progress(line: str) -> Optional[Dict]:
        """解析烧录进度: Writing at 0x001b25d3... (66 %)"""
        match = re.search(r'Writing at 0x[0-9a-f]+\.\.\. \((\d+) %\)', line)
        if match:
            percentage = int(match.group(1))
            return {
                'stage': 'flashing',
                'percentage': percentage,
                'message': line.strip()
            }
        return None

    @staticmethod
    def extract_errors(log_lines: List[str]) -> List[str]:
        """提取错误信息"""
        errors = []
        for line in log_lines:
            if 'error:' in line.lower() or line.strip().startswith('E ('):
                errors.append(line.strip())
        return errors

    @staticmethod
    def extract_warnings(log_lines: List[str]) -> List[str]:
        """提取警告信息"""
        warnings = []
        for line in log_lines:
            if 'warning:' in line.lower() or line.strip().startswith('W ('):
                warnings.append(line.strip())
        return warnings[:20]  # 最多20条

    @staticmethod
    def extract_binary_size(log_lines: List[str]) -> Optional[str]:
        """提取二进制大小"""
        for line in log_lines:
            match = re.search(r'binary size (0x[0-9a-f]+) bytes', line)
            if match:
                return match.group(1)
        return None
