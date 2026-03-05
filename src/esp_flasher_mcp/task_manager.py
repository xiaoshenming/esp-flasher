"""任务管理器 - 管理异步构建/烧录任务"""
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from .tmux_manager import TmuxManager

class TaskManager:
    def __init__(self, project_path: str, project_name: str):
        self.project_path = Path(project_path)
        self.project_name = project_name
        self.log_dir = self.project_path / "build" / "flasher-logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.tmux = TmuxManager()
        self.session_name = self.tmux.get_session_name(project_name)

    def _get_task_id(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _get_log_path(self, task_id: str, operation: str) -> Path:
        return self.log_dir / f"{task_id}_{operation}.log"

    def _capture_tmux_output(self) -> str:
        """捕获 tmux session 输出"""
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", self.session_name, "-p"],
            capture_output=True, text=True
        )
        return result.stdout if result.returncode == 0 else ""

    def start_build_flash_monitor(self, clean: bool = False) -> Dict:
        """启动编译+烧录+监控"""
        task_id = self._get_task_id()

        # 创建或复用 tmux session
        self.tmux.create_session(self.session_name, str(self.project_path))

        # 退出可能存在的 monitor
        self.tmux.send_ctrl_bracket(self.session_name)

        # 构建命令
        cmd = "conda activate idf55 && source /opt/esp-idf/export.sh && "
        if clean:
            cmd += "idf.py fullclean && "
        cmd += "idf.py build && idf.py flash monitor"

        # 发送命令
        self.tmux.send_keys(self.session_name, cmd)

        return {
            "task_id": task_id,
            "status": "running",
            "project": str(self.project_path),
            "tmux_session": self.session_name,
            "log_file": str(self._get_log_path(task_id, "build_flash_monitor"))
        }

    def get_current_output(self) -> str:
        """获取当前 tmux 输出"""
        return self._capture_tmux_output()

    def save_log(self, task_id: str, operation: str, content: str, summary: Dict):
        """保存日志和摘要"""
        log_path = self._get_log_path(task_id, operation)
        log_path.write_text(content)

        summary_path = self.log_dir / f"{task_id}_{operation}_summary.json"
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))

        # 更新 latest.json
        latest_path = self.log_dir / "latest.json"
        latest_path.write_text(json.dumps({
            "task_id": task_id,
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "log_file": str(log_path),
            "summary_file": str(summary_path)
        }, indent=2))
