# ESP Flasher MCP

ESP32 编译/烧录/监控自动化 MCP 工具。

## 功能

- 自动检测 ESP-IDF 项目
- 一键编译 + 烧录 + 监控
- tmux 集成（用户可随时 attach 查看）
- 流式进度通知
- 日志保存和解析（编译错误、烧录进度、设备启动状态）

## 安装

```bash
# 使用 uvx 直接运行（推荐）
uvx --from /home/ming/tools/esp-flasher-mcp esp-flasher-mcp

# 或者 pip 安装
pip install -e /home/ming/tools/esp-flasher-mcp
```

## Claude Code 配置

在 `~/.claude/settings.json` 中添加：

```json
{
  "mcpServers": {
    "esp-flasher": {
      "command": "uvx",
      "args": ["--from", "/home/ming/tools/esp-flasher-mcp", "esp-flasher-mcp"]
    }
  }
}
```
