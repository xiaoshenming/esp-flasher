"""ESP Flasher MCP Server"""
import json
from typing import Optional
from fastmcp import FastMCP
from .detector import ESPProjectDetector
from .task_manager import TaskManager
from .log_parser import LogParser

mcp = FastMCP("esp-flasher")

# 全局任务管理器
_task_manager: Optional[TaskManager] = None


def _get_or_create_manager(project_path: Optional[str] = None) -> TaskManager:
    global _task_manager
    project = ESPProjectDetector.detect(project_path)
    if not project:
        raise ValueError("未检测到 ESP-IDF 项目，请确认路径包含 CMakeLists.txt 和 main/ 目录")
    _task_manager = TaskManager(project['path'], project['name'])
    return _task_manager


@mcp.tool()
def build(project_path: Optional[str] = None) -> str:
    """编译 ESP32 项目

    Args:
        project_path: 项目路径，留空则自动检测当前目录
    """
    mgr = _get_or_create_manager(project_path)
    result = mgr.start_operation("build")
    return json.dumps(result, indent=2)


@mcp.tool()
def flash(project_path: Optional[str] = None) -> str:
    """烧录固件到 ESP32 设备

    Args:
        project_path: 项目路径，留空则自动检测当前目录
    """
    mgr = _get_or_create_manager(project_path)
    result = mgr.start_operation("flash")
    return json.dumps(result, indent=2)


@mcp.tool()
def monitor(project_path: Optional[str] = None) -> str:
    """启动串口监控，查看设备日志

    Args:
        project_path: 项目路径，留空则自动检测当前目录
    """
    mgr = _get_or_create_manager(project_path)
    result = mgr.start_operation("monitor")
    return json.dumps(result, indent=2)


@mcp.tool()
def build_flash_monitor(
    project_path: Optional[str] = None,
    clean: bool = False
) -> str:
    """一键编译、烧录、监控 ESP32 项目（最常用）

    Args:
        project_path: 项目路径，留空则自动检测当前目录
        clean: 是否先执行 fullclean
    """
    mgr = _get_or_create_manager(project_path)
    result = mgr.start_build_flash_monitor(clean=clean)
    return json.dumps(result, indent=2)


@mcp.tool()
def fullclean(project_path: Optional[str] = None) -> str:
    """完全清理构建目录

    Args:
        project_path: 项目路径，留空则自动检测当前目录
    """
    mgr = _get_or_create_manager(project_path)
    result = mgr.start_operation("fullclean")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_device_output(
    project_path: Optional[str] = None,
    lines: int = 80
) -> str:
    """获取设备当前输出（tmux 窗口内容）

    Args:
        project_path: 项目路径，留空使用当前任务
        lines: 返回最近多少行，默认80
    """
    global _task_manager
    if not _task_manager and project_path:
        _get_or_create_manager(project_path)
    if not _task_manager:
        return json.dumps({"error": "没有活动的任务，请先调用 build_flash_monitor"})

    output = _task_manager.get_current_output(lines=lines)
    log_lines = output.strip().split('\n')
    errors = LogParser.extract_errors(log_lines)
    warnings = LogParser.extract_warnings(log_lines)
    binary_size = LogParser.extract_binary_size(log_lines)

    summary = {
        "tmux_session": _task_manager.session_name,
        "errors": errors,
        "warnings_count": len(warnings),
        "binary_size": binary_size,
    }
    return f"=== 摘要 ===\n{json.dumps(summary, indent=2, ensure_ascii=False)}\n\n=== 输出 ===\n{output}"


@mcp.tool()
def get_log(
    project_path: Optional[str] = None,
    task_id: Optional[str] = None
) -> str:
    """获取历史构建/烧录日志

    Args:
        project_path: 项目路径，留空使用当前任务
        task_id: 任务ID，留空则返回最近一次
    """
    global _task_manager
    if not _task_manager and project_path:
        _get_or_create_manager(project_path)
    if not _task_manager:
        return json.dumps({"error": "没有活动的任务"})

    latest_file = _task_manager.log_dir / "latest.json"
    if latest_file.exists():
        latest = json.loads(latest_file.read_text())
        log_file = latest.get("log_file", "")
        summary_file = latest.get("summary_file", "")
        from pathlib import Path
        result = {"latest": latest}
        if Path(log_file).exists():
            result["log_tail"] = Path(log_file).read_text()[-3000:]
        if Path(summary_file).exists():
            result["summary"] = json.loads(Path(summary_file).read_text())
        return json.dumps(result, indent=2, ensure_ascii=False)

    return json.dumps({"error": "没有历史日志"})


def main():
    mcp.run(transport="stdio")
