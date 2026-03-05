"""ESP Flasher MCP Server"""
from mcp.server import Server
from mcp.types import Tool, TextContent
from .detector import ESPProjectDetector
from .task_manager import TaskManager
from .log_parser import LogParser
import json

app = Server("esp-flasher")

# 全局任务管理器
current_task_manager = None

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="build_flash_monitor",
            description="一键编译、烧录、监控ESP32项目",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "项目路径，留空则自动检测"
                    },
                    "clean": {
                        "type": "boolean",
                        "description": "是否先执行fullclean",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="get_device_output",
            description="获取设备当前输出（monitor内容）",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    global current_task_manager

    if name == "build_flash_monitor":
        # 检测项目
        project = ESPProjectDetector.detect(arguments.get("project_path"))
        if not project:
            return [TextContent(type="text", text=json.dumps({
                "error": "未检测到ESP-IDF项目"
            }))]

        # 创建任务管理器
        current_task_manager = TaskManager(project['path'], project['name'])

        # 启动任务
        result = current_task_manager.start_build_flash_monitor(
            clean=arguments.get("clean", False)
        )

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_device_output":
        if not current_task_manager:
            return [TextContent(type="text", text=json.dumps({
                "error": "没有活动的任务"
            }))]

        output = current_task_manager.get_current_output()
        return [TextContent(type="text", text=output)]

    return [TextContent(type="text", text=json.dumps({"error": "未知工具"}))]

def main():
    import asyncio
    asyncio.run(app.run())

