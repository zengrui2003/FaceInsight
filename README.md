# FaceInsight 人脸颜值数据分析系统

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

FaceInsight 是一个基于 Python 的人脸图像采集与颜值数据分析桌面应用。项目支持通过关键词自动采集图片，也支持直接分析本地图片文件夹；检测到人脸后调用百度智能云人脸检测服务，将 `beauty` 分数转换为 `1-10` 分区间，并通过 SQLite 与 pyecharts 完成数据存储、统计、历史查询和可视化。

> 颜值分数具有强烈的主观性，本项目仅用于技术学习、课程展示和数据分析实验，不应作为评价个人的依据。

## 功能特性

- 使用 `icrawler` 按关键词从 Bing 采集图片，并自动过滤常见图片格式。
- 支持分析本地图片文件夹，便于在爬虫不可用时进行演示。
- 调用百度智能云人脸检测接口，获取年龄、表情和颜值等字段。
- 将颜值结果按 `1-10` 分进行分段统计，`0` 表示未检测到人脸。
- 使用 SQLite 保存每次分析记录，支持重新查询和导出 CSV。
- 使用 pyecharts 生成分数柱状图、占比环图、颜值仪表盘和历史趋势图。
- 提供综合数据大屏，包括平均分趋势、人脸检出分布、关键词对比和分数雷达图。
- 使用 tkinter 构建深色桌面界面，通过后台线程执行分析并实时显示任务进度。
- 支持使用 PyInstaller 与 Inno Setup 构建 Windows 可执行程序和安装包。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 桌面界面 | tkinter / ttk |
| 图片采集 | icrawler |
| 人脸分析 | 百度智能云人脸检测 API |
| 数据存储 | SQLite |
| 数据可视化 | pyecharts |
| 图片处理 | Pillow |
| 打包 | PyInstaller / Inno Setup |

## 环境要求

- Python 3.10 或更高版本
- 可访问互联网
- 百度智能云账号，并已开通人脸检测服务
- Windows 10/11；核心业务代码可跨平台运行，当前界面和安装脚本主要面向 Windows

## 快速开始

### 1. 克隆仓库

```powershell
git clone https://github.com/zengrui2003/FaceInsight.git
cd FaceInsight
```

### 2. 创建虚拟环境并安装依赖

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

如果 PowerShell 禁止运行激活脚本，可以临时执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 3. 配置百度智能云

在百度智能云控制台创建应用并获取：

- `APP_ID`
- `API_KEY`
- `SECRET_KEY`

推荐使用环境变量，避免密钥写入项目文件：

```powershell
$env:BAIDU_APP_ID="你的 APP_ID"
$env:BAIDU_API_KEY="你的 API_KEY"
$env:BAIDU_SECRET_KEY="你的 SECRET_KEY"
```

也可以复制配置模板：

```powershell
Copy-Item config.local.json.example config.local.json
```

然后填写真实的 `app_id`、`api_key` 和 `secret_key`。

> `config.local.json` 已加入 `.gitignore`。请勿将真实密钥、Token 或其他凭据提交到公开仓库。

### 4. 启动程序

```powershell
python main.py
```

## 使用说明

1. 选择“Bing 爬虫”并输入关键词和采集数量，程序会自动下载图片。
2. 或选择“本地文件夹”，指定包含待分析图片的目录。
3. 点击开始分析，等待图片采集、人脸检测和结果统计完成。
4. 分析结果会写入 `beauty_analysis.db`，图表和报告输出到 `exports/`。
5. 在主界面查看历史记录、导出 CSV，或生成多维历史数据大屏。

## 数据定义

- `0`：未检测到人脸。
- `1-10`：百度人脸检测返回的 `beauty` 分数映射后的区间。
- 平均颜值只统计检测到人脸的图片。
- 如果所有图片均未检测到人脸，平均值为 `NULL`，界面显示“无有效人脸”。

## 测试

安装开发依赖后运行测试：

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

当前测试覆盖分数聚合、平均值计算和无人脸时的除零保护。

## Windows 打包

安装 [PyInstaller](https://pyinstaller.org/) 和 [Inno Setup 6](https://jrsoftware.org/isinfo.php) 后，在项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File installer\build_installer.ps1
```

构建产物位于：

- `dist/FaceInsight/`
- `installer/output/FaceInsightSetup.exe`

打包后的程序同样优先读取环境变量，也支持读取与可执行文件同级的 `config.local.json`。

## 项目结构

```text
FaceInsight/
├── face_insight/
│   ├── app.py              # tkinter 桌面界面与任务调度
│   ├── charts.py           # 分析图表和历史大屏
│   ├── config.py           # 百度 API 配置加载
│   ├── crawler.py          # 图片采集与格式过滤
│   ├── face_analysis.py    # 人脸检测与分数聚合
│   └── storage.py          # SQLite 数据访问
├── installer/              # PyInstaller / Inno Setup 构建脚本
├── scripts/                # 演示文稿生成等辅助脚本
├── tests/                  # 自动化测试
├── config.local.json.example
├── FaceInsight.spec
├── main.py
├── requirements.txt
└── README.md
```

## 常见问题

### 百度接口返回 `Open api qps request limit reached`

这是接口限流。程序会自动等待并重试；如果频繁出现，可以增大 `FaceAnalyzer` 的 `request_interval`。

### 返回 `IAM Certification failed`

请检查 `APP_ID`、`API_KEY` 和 `SECRET_KEY` 是否正确，并确认对应应用已开通人脸检测服务。

### 图片无法检测

百度接口不接受超过 10 MB 的图片。请压缩图片或降低采集图片的尺寸。

### 没有采集到图片

Bing 的页面结构或网络状态可能影响采集结果。可以更换关键词，或改用“本地文件夹”模式。

## 已知限制

- 每个分析任务当前以图片为基本单位，主要分析检测到的第一张人脸。
- 颜值分数依赖第三方 API，结果会受图片质量、角度、光照和服务策略影响。
- 采集图片来源不受项目控制，使用者应自行确认版权、隐私和平台规则。
- 项目未包含真实凭据、历史数据库、下载图片、导出文件或预构建安装包。

## 许可证

本项目采用 [MIT License](LICENSE) 开源。