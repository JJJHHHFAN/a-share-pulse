# a-share-pulse 维护实现计划

> 在当前会话内逐任务执行；用户已授权继续和同步。优先复用现有干净工作区。

**目标：** 修复已确认的问题并建立自动回归检查。

**架构：** 保留现有运行方式，测试与发布各自独立；只修改已确认范围。

**技术栈：** Python、GitHub Actions；沿用各项目依赖。

## 文件与步骤
- [x] 创建 `tests/test_local_schedule.py`：临时目录复制脚本，使用真实 zsh 与可控日期/无网络 git 命令，验证上海时区的收盘前、收盘后、周末及跨日归档检查。
- [x] 执行 `.venv/bin/python -m unittest discover -s tests -v`，先观察宿主 America/Los_Angeles 时区下应抓取却跳过的失败。
- [x] 在 `scripts/update_local.sh` 的 `set -euo pipefail` 后添加 `export TZ=Asia/Shanghai`。
- [x] 修改 `.github/workflows/daily.yml`，push 路径使用 `docs/**` 和该发布工作流路径。
- [x] 创建 `tests/test_snapshot_files.py`：读取真实已有文件，检查 latest/history/market.js 的一致性和有限数值；不访问外网。
- [x] 创建 `.github/workflows/test.yml`：push、pull_request、手动；Python 3.12；安装 requirements；安装 zsh；运行 unittest 和 `zsh -n scripts/update_local.sh scripts/install_local_schedule.sh`。
- [ ] 更新 README。执行完整测试、脚本语法与浏览器页面检查，白名单提交推送并验证自动检查及 Pages 发布。

## 本地验证记录

2026-11-05：本地测试与相关检查已完成；远端同步及自动运行结果由交付报告记录。复选框记录本次实施内容，最终结果以交付报告为准。
