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
    print("Error: DAYTONA_API_KEY was not found. Set it in one of these ways:")
    print("  1. Create a .env file with: DAYTONA_API_KEY=your-api-key")
    print("  2. Set DAYTONA_API_KEY in the environment")
    print("  3. Install python-dotenv: pip install python-dotenv")
    sys.exit(1)

config = DaytonaConfig(api_key=api_key)

daytona = Daytona(config)

# Create a sandbox
sandbox = daytona.create()

# Run code inside the sandbox
response = sandbox.process.code_run('print("Hello World from code!")')
if response.exit_code != 0:
  print(f"Error: {response.exit_code} {response.result}")
else:
    print(response.result)
