from fastchat.conversation import Conversation
from fastchat import conversation as conv
from fastchat.serve.base_model_worker import BaseModelWorker
import sys
from typing import List, Dict
import uuid
from zhipuai import ZhipuAI
import json
from dotenv import load_dotenv
load_dotenv()


class ChatGLMWorker(BaseModelWorker):
    def __init__(
        self,
        *,
        model_names: List[str] = ["chatGLM-130B"],
        controller_addr: str = None,
        worker_addr: str = None,
        version: str = "glm-4",
        **kwargs,
    ):
        kwargs.setdefault("worker_id", uuid.uuid4().hex[:8])
        kwargs.setdefault("model_path", "")
        kwargs.setdefault("limit_worker_concurrency", 5)
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        super().__init__(**kwargs)
        self.context_len = 32768
        self.version = version
        self.client = ZhipuAI()
        self.init_heart_beat()

    def count_token(self, params):
        prompt = params["prompt"]
        return {"count": len(str(prompt)), "error_code": 0}

    def generate_stream_gate(self, params: Dict):
        self.call_ct += 1
        try:
            messages = [{'role': 'user', 'content': params.get('prompt')}]
            res = self.client.chat.completions.create(
                model=self.version,
                messages=messages,
                stream=True,
                temperature=params.get('temperature')
            )
            text = ''
            for chunk in res:
                text += chunk.choices[0].delta.content
                finish_reason = chunk.choices[0].finish_reason
                yield json.dumps({"error_code": 0, "text": text, "finish_reason": finish_reason}).encode() + b'\0'
        except Exception as e:
            yield json.dumps({"error_code": 500, "text": e.str()}).encode() + b'\0'

    def generate_gate(self, params):
        self.call_ct += 1
        try:
            messages = [{'role': 'user', 'content': params.get('prompt')}]
            res = self.client.chat.completions.create(
                model=self.version,
                messages=messages,
                temperature=params.get('temperature')
            )
            text = res.choices[0].message.content
            return {"error_code": 0, "text": text, "finish_reason": "stop"}
        except Exception as e:
            return {"error_code": 500, "text": str(e)}

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        return conv.Conversation(
            name=self.model_names[0],
            system_message="你是一个聪明的助手，请根据用户的提示来完成任务",
            messages=[],
            roles=["Human", "Assistant", "System"],
            sep="\n###",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from fastchat.serve.model_worker import app

    worker = ChatGLMWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21001",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    uvicorn.run(app, port=21001)
