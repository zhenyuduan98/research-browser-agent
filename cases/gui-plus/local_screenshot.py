import os
import base64
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


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


image_path = "ctrip_page.png"
image_data_url = f"data:image/png;base64,{encode_image(image_path)}"

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": image_data_url}},
            {"type": "text", "text": "Select January 30 as the departure date."},
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
