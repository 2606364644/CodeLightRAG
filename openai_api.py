import json
import requests
from loguru import logger


class OpenaiApiClient:

    def __init__(self, base_url, api_key, model_name):
        self.base_url = base_url
        self.model_name = model_name
        self.timeout = 3000  # 设置超时时间为 300 秒（5 分钟）
        self._headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

    def _req(self, prompt: str, system_prompt: str = None) -> str:
        messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        if system_prompt:
            messages.insert(0, {
                "role": "system",
                "content": system_prompt             
            })
        payload = json.dumps({
            "model": self.model_name,
            "messages": messages
        })

        response = requests.post(f"{self.base_url}/chat/completions", headers=self._headers, data=payload)
        if response.status_code == 200:
            data = json.loads(response.text)
            content = data["choices"][0]["message"]["content"]
            return content
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def req_common(self, prompt: str, system_prompt: str = None) -> str:
        for _ in range(5):
            try:
                return self._req(prompt, system_prompt)
            except Exception as e:
                logger.exception(e)
                continue

