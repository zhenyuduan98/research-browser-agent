import os
from openai import OpenAI

SYSTEM_PROMPT = """You are a GUI action agent. Look at a screenshot, follow the user instruction, and return exactly one JSON object for the next atomic GUI action. No text before or after the JSON.

Rules:
- action must be one of CLICK, TYPE, SCROLL, KEY_PRESS, FINISH, FAIL.
- parameters must match the action:
  - CLICK: {"x": <int>, "y": <int>, "description": "<what you clicked>"}
  - TYPE: {"text": "<string>", "needs_enter": <bool>}
  - SCROLL: {"direction": "up" or "down", "amount": "small", "medium", or "large"}
  - KEY_PRESS: {"key": "<string, e.g. enter, esc, alt+f4>"}
  - FINISH: {"message": "<what was completed>"}
  - FAIL: {"reason": "<why it cannot be done>"}
Only click something you can see in the screenshot.
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://img.alicdn.com/imgextra/i2/O1CN016iJ8ob1C3xP1s2M6z_!!6000000000026-2-tps-3008-1758.png"
                },
            },
            {"type": "text", "text": "Open the browser."},
        ],
    },
]

client = OpenAI(
    # Or set api_key="sk-xxx" here if DASHSCOPE_API_KEY is not in the environment.
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="gui-plus",
    messages=messages,
)
print(completion.choices[0].message.content)
