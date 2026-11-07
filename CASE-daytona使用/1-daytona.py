from daytona_sdk import Daytona, DaytonaConfig
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

api_key = os.getenv("DAYTONA_API_KEY")
if not api_key:
    print("错误: 未找到 DAYTONA_API_KEY。请通过以下方式之一设置:")
    print("  1. 创建 .env 文件，添加: DAYTONA_API_KEY=your-api-key")
    print("  2. 在系统环境变量中设置 DAYTONA_API_KEY")
    print("  3. 安装 python-dotenv: pip install python-dotenv")
    sys.exit(1)

config = DaytonaConfig(api_key=api_key)

daytona = Daytona(config)

# 创建沙箱实例
sandbox = daytona.create()

# 在沙箱中安全地运行代码
response = sandbox.process.code_run('print("Hello World from code!")')
if response.exit_code != 0:
  print(f"错误: {response.exit_code} {response.result}")
else:
    print(response.result)
