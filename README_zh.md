# 研究型浏览器 Agent

[English](README.md)

这是一个浏览器 Agent，用来帮用户完成原本要自己打开网页、填表、读结果的研究任务。

包含两个案例：

- **案例 1：竞品分析。** 打开竞品网站，把定位、功能和公开价格整理成一份对比。
- **案例 2：携程机票查询。** 在携程机票页上操作，查询航班，例如圣诞节飞悉尼。

运行时基于 [OpenManus](https://github.com/FoundationAgents/OpenManus)（MIT）。本仓库在此之上做的是研究流程：Web 控制台、出行知识库、页面元素读不到时的视觉兜底，以及上面两个案例。

## 架构

![架构](docs/architecture.svg)

循环本身是 think、act，然后检查要不要停。图里补上了原先时序图没画出来的三块：

- 任务可以从 `python main.py` 进入，也可以从 `python app.py` 进入。网页控制台用 SSE 把每一步 think 和 act 推到页面上，不是只等最后一句。
- 每次调用模型还会带上系统提示词：角色说明、`knowledge/*.txt` 和当前时间。`OpenManus-rag` 的知识库里写了携程列表页的直达地址。
- `browser_use` 用 Playwright 打开一个可见的 Chromium。DOM 快照里没有元素时，GUI-Plus 看截图，返回点击或输入。截图可以写进下一条记忆。需要隔离执行的代码可以走 Daytona 沙箱，而不是本机的 `python_execute`。

循环在三种情况下结束：调用 `terminate`、达到 `max_steps`、或 token 超出上限。连续出现相同回复时，会追加一条“换策略”的提示。`max_steps` 在 `OpenManus-rag` 是 20，在 `OpenManus-gui` 是 30，在 `OpenManus-cy` 是 50。

| 目录 | 作用 |
| --- | --- |
| `OpenManus-cy` | Agent 循环、工具，以及 Daytona 沙箱 |
| `OpenManus-gui` | FastAPI 控制台，用来逐步看一次任务 |
| `OpenManus-rag` | 启动前把 `knowledge/*.txt` 注入系统提示词 |
| `cases/gui-plus` | 单独调用视觉模型，让它返回一个 GUI 动作 |
| `cases/daytona` | 在 Daytona 沙箱里跑一段代码 |

系统提示词要求：机票价格、竞品说法这类实时信息必须来自工具返回，不能编造。

## 案例 1：竞品分析

让 Agent 比较同一品类里的几个产品。它先找到官网，再逐个打开，抽取定位、功能列表和公开价格，最后写成一份对照说明。

示例提示：

```text
对比 Notion、Coda 和 Outline 的定位、核心功能和公开价格。每一点都写上来源页面。
```

一次运行里会发生这些事：

1. 规划器把任务拆成「一次只看一个网站」。
2. `web_search` 找到官网。
3. `browser_use` 打开页面。如果 DOM 里没有可用元素，GUI-Plus 会看截图，返回点击或输入。
4. 最终回复是基于这些页面的对比，而不是一段泛泛的产品介绍。

## 案例 2：携程机票查询

让 Agent 在携程上查机票。实际跑过的提示是：

```text
搜索圣诞节飞悉尼的携程机票
```

一次运行里会发生这些事：

1. Agent 打开 `https://flights.ctrip.com/`。
2. 填写出发城市和到达城市。这个页面的输入框经常不在 DOM 快照里，于是视觉模型点击城市框再输入城市名。
3. `OpenManus-rag/knowledge/travel_tools.txt` 还写了携程列表页的直达地址（`oneway-{出发}-{到达}?depdate=YYYY-MM-DD`）。城市代码和日期已经确定时，可以跳过日历控件。

浏览器配置是 `headless = false`，窗口可见，方便看每一步。

## 运行

使用 Python 3.12。依赖安装一次即可：

```bash
pip install -r OpenManus-gui/requirements.txt
python -m playwright install chromium
```

密钥放在环境变量里，不要写进会提交的文件。

```bash
# PowerShell
$env:DASHSCOPE_API_KEY = "your-dashscope-key"
$env:DAYTONA_API_KEY = "your-daytona-key"   # 只有沙箱示例需要
```

网页控制台：

```bash
cd OpenManus-gui
python app.py
```

打开 http://localhost:5172 ，输入案例里的提示。`OpenManus-rag` 是带知识库的同一个 Agent：

```bash
cd OpenManus-rag
python main.py
```

只检查视觉模型：

```bash
cd cases/gui-plus
python remote_screenshot.py
```

检查沙箱：先把 `cases/daytona/.env.example` 复制成 `.env` 并填入 Key，然后：

```bash
cd cases/daytona
python sandbox_hello.py
```

## 配置

`config/config.toml` 在 `.gitignore` 里，不会上传。把 `config/config.example.toml` 复制成 `config/config.toml`，`api_key` 留空，或只在自己的电脑上填写。`api_key` 为空时，进程读取环境变量 `DASHSCOPE_API_KEY`。默认对话模型是 `qwen-max`，视觉模型是 `qwen-vl-plus`，都走百炼的 OpenAI 兼容接口。`cases/daytona/.env` 同样被忽略，从 `.env.example` 复制一份再填写。

## 致谢

Agent 循环、工具协议和浏览器工具结构来自 MetaGPT / FoundationAgents 社区的 [OpenManus](https://github.com/FoundationAgents/OpenManus)，许可证为 MIT。见 `OpenManus-cy/LICENSE`。
