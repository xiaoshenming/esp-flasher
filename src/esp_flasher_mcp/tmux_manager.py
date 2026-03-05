"""Tmux session 管理"""
import subprocess
import time
from typing import Optional

class TmuxManager:
    @staticmethod
    def get_session_name(project_name: str) -> str:
        return f"esp-flasher-{project_name}"

    @staticmethod
    def session_exists(session_name: str) -> bool:
        result = subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            capture_output=True
        )
        return result.returncode == 0

    @staticmethod
    def create_session(session_name: str, project_path: str) -> None:
        """创建 tmux session（确保 uucp 组权限用于串口访问）"""
        if not TmuxManager.session_exists(session_name):
            # 使用 sg uucp 启动 session，确保串口权限
            subprocess.run([
                "tmux", "new-session", "-d", "-s", session_name,
                "-c", project_path,
                "sg", "uucp", "-c", "zsh"
            ], check=True)

    @staticmethod
    def send_keys(session_name: str, command: str) -> None:
        """发送命令到 tmux session"""
        subprocess.run([
            "tmux", "send-keys", "-t", session_name, command, "C-m"
        ], check=True)

    @staticmethod
    def send_ctrl_bracket(session_name: str) -> None:
        """发送 Ctrl+] 退出 monitor"""
        subprocess.run([
            "tmux", "send-keys", "-t", session_name, "C-]"
        ], check=True)
