from typing import Optional, List, Mapping, Any
from langchain.llms.base import LLM
import requests
import os
from dotenv import load_dotenv
load_dotenv()


# 自定义 DeepSeek LLM 类
class QWENCoderLLM(LLM):
    model_name: str = "Qwen/Qwen2.5-Coder-7B-Instruct"
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
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=50)
            response.raise_for_status()  # 检查 HTTP 状态码是否为 4xx 或 5xx
            try:
                return response.json()["choices"][0]["message"]["content"]
            except (ValueError, KeyError) as e:
                raise Exception(f"解析 JSON 响应失败：{e}")
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请检查网络连接或增加超时时间。")
        except requests.exceptions.ConnectionError:
            raise Exception("网络连接错误，请检查网络状态或 API 地址是否正确。")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败：{e}")
        
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model_name": self.model_name}

    @property
    def _llm_type(self) -> str:
        return "qwen"
    

class GLMLLM(LLM):
    model_name: str = "THUDM/glm-4-9b-chat"
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
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=50)
            response.raise_for_status()  # 检查 HTTP 状态码是否为 4xx 或 5xx
            try:
                return response.json()["choices"][0]["message"]["content"]
            except (ValueError, KeyError) as e:
                raise Exception(f"解析 JSON 响应失败：{e}")
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请检查网络连接或增加超时时间。")
        except requests.exceptions.ConnectionError:
            raise Exception("网络连接错误，请检查网络状态或 API 地址是否正确。")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败：{e}")
        
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model_name": self.model_name}

    @property
    def _llm_type(self) -> str:
        return "glm"
