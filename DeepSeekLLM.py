from typing import Optional, List, Mapping, Any
from langchain.llms.base import LLM
import requests
import os
from dotenv import load_dotenv
load_dotenv()
# 自定义 DeepSeek LLM 类
class DeepSeekLLM(LLM):
    model_name: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
    api_key: str = os.getenv("DEEPSEEK_API_KEY")
    base_url: str = os.getenv("DEEPSEEK_API_URL")

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        response = requests.post(self.base_url, headers=headers, json=data)
        if response.status_code == 200:
            try:
                return response.json()["choices"][0]["message"]["content"]
            except (ValueError, KeyError) as e:
                raise Exception(f"解析 JSON 响应失败：{e}")
        else:
            raise Exception(f"DeepSeek API 调用失败：{response.status_code}, {response.text}")
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model_name": self.model_name}

    @property
    def _llm_type(self) -> str:
        return "deepseek"