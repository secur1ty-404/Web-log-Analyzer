# Web日志分析工具 🕵️

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-%E6%AC%A2%E8%BF%8E%E6%8F%90%E4%BA%A4-brightgreen.svg)](https://github.com/yourname/web-log-analyzer/pulls)


> 一款高效的Web服务器日志图形化分析工具，支持多条件组合查询与智能过滤

## 目录 📚

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [注意事项](#注意事项)
- [开发路线](#开发路线)
- [参与贡献](#参与贡献)
- [许可证](#许可证)

## 功能特性 🚀

### 核心功能

- 🔍 **智能搜索**：支持AND逻辑多关键词搜索，历史记录自动补全
- ⏰ **时间过滤**：预设最近24小时范围，支持自定义时间区间
- 🚫 **高级过滤**：排除指定文件类型（.js/.css）、端口、状态码
- 📊 **结果展示**：关键字段高亮，自动统计匹配量

### 性能表现

| 日志规模 | 处理速度 | 内存占用 |
| -------- | -------- | -------- |
| 10万行   | <3秒     | ~200MB   |
| 50万行   | ~15秒    | ~800MB   |
| 100万行  | ~30秒    | ~1.5GB   |

## 快速开始 🚴

### 环境要求

- Python 3.8+
- 支持系统：Windows 10+/macOS 10.15+/Linux Ubuntu 18.04+

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yourname/web-log-analyzer.git

# 安装依赖
pip install -r requirements.txt

# 启动程序
python main.py

```

## 使用指南 📖

### 界面布局

1. 文件控制区：上传日志文件（支持拖放）

2. 过滤条件区：

   ​	精确关键词（支持,分隔多条件）

   ​	时间选择器（格式：YYYY-MM-DD HH:MM:SS）

3. 结果展示区：右键菜单支持复制/导出选中内容

典型场景
场景1：检测异常登录

1. 关键词：admin,login
2. 状态码：401,403
3. 时间范围：最近24小时

场景2：分析大文件下载

1. 排除类型：.jpg,.mp4
2. 状态码：206（部分内容）
3. 端口：8080,8090

##### 界面布局截图 

[![GUI界面截图](https://raw.githubusercontent.com/M1nkit/Web-log-Analyzer/main/template.png)](https://raw.githubusercontent.com/M1nkit/Web-log-Analyzer/main/template.png)

## 注意事项 ⚠️

#### 日志格式要求

格式示例：
114.248.123.45 - [15/Aug/2023:14:23:45 +0800] 200 0.002 1024 "GET /index.html HTTP/1.1" 1.001

必须包含字段：

- [ ] 客户端IP
- [ ] 时间戳（dd/MMM/yyyy:HH:mm:ss Z）
- [ ] 状态码
- [ ] 请求路径
- [ ] 后端端口

#### 常见问题

Q：处理大文件时内存不足？
A：建议使用以下命令预处理日志：

​    #分割100MB的日志文件

​	  split -b 100M access.log access_part_

Q：时间过滤不生效？
A：请检查时区设置，示例日志使用+0800时区，工具会自动转换UTC时间

## 开发路线 🛠️

| 版本 | 主要功能                     | 进度     |
| ---- | ---------------------------- | -------- |
| v1.0 | 整体视图设计                 | ✅ 已完成 |
| v1.1 | 适配多种Web日志              | 🚧 开发中 |
| v2.0 | 集成可视化图表（访问趋势图） | ⌛ 规划中 |

## 参与贡献 🤝

欢迎通过以下方式参与项目：
提交Issues 反馈问题
Fork仓库并提交Pull Request
完善文档或翻译多语言版本

## 许可证 📜

本项目采用 MIT License，您可以在遵守许可条款的前提下自由使用。
星光不问赶路人，时光不负有心人 ✨
持续优化中，期待您的✨星星✨支持！
