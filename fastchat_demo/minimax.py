from fastchat.conversation import Conversation
from fastchat import conversation as conv
from fastchat.serve.base_model_worker import BaseModelWorker
import sys
from typing import List, Dict
import uuid
import requests
import json
# from dotenv import load_dotenv
# load_dotenv()


class MiniMaxWorker(BaseModelWorker):
    def __init__(
        self,
        *,
        model_names: List[str] = ["MiniMax"],
        controller_addr: str = None,
        worker_addr: str = None,
        version: str = "abab5.5-chat",
        **kwargs,
    ):
        kwargs.setdefault("worker_id", uuid.uuid4().hex[:8])
        kwargs.setdefault("model_path", "")
        kwargs.setdefault("limit_worker_concurrency", 5)
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        super().__init__(**kwargs)
        self.init_heart_beat()
        self.context_len = 32768
        self.version = version
        group_id = "1754037872157003786"
        self.url = f"https://api.minimax.chat/v1/text/chatcompletion_pro?GroupId={group_id}"
        api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJJVCIsIlVzZXJOYW1lIjoiSVQiLCJBY2NvdW50IjoiIiwiU3ViamVjdElEIjoiMTc1NDAzNzg3MjE2MTE5ODA5MCIsIlBob25lIjoiMTU2MTg1MzcwOTUiLCJHcm91cElEIjoiMTc1NDAzNzg3MjE1NzAwMzc4NiIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6IiIsIkNyZWF0ZVRpbWUiOiIyMDI0LTAyLTA1IDA1OjA3OjUzIiwiaXNzIjoibWluaW1heCJ9.PN1_pWeK4wPLWqWDzoPKHwZaiUl4sxyRx94NUde22XtdQoVFwz66JEO_38VLGdFhkiK8Zl91edDctkgR_p5ORAMRmcjFL2TFMobVJg5Dm1fhcdeocePYVoIWg0bWEHtTyD0DCXqJftqcjU_YLnO4K0UjIEQDfqr5m2TREHGkLCSFwvlx-onDS9QQkKwg70L5IZuO49vhsvBrXAG-Z5clnHNIGSpWnXpUE9WPKLrWKcVv4Z5oHltIZHSkrCT4Sq4dx2dvunBx1808qFG-vRCcPHdECopZ_GYiHtom9szk5nVywfy0AqEZAOSPmDYqbka7CnxYPt1dMdmP_kCREY3PLg"
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        self.payload = {
            "model": self.version,
            "tokens_to_generate": 1024,
            "reply_constraints": {"sender_type": "BOT", "sender_name": "MM智能助理"},
            "bot_setting": [
                {
                    "bot_name": "MM智能助理",
                    "content": "MM智能助理是一款由MiniMax自研的，没有调用其他产品的接口的大型语言模型。MiniMax是一家中国科技公司，一直致力于进行大模型相关的研究。",
                }
            ],
        }

    def count_token(self, params):
        prompt = params["prompt"]
        return {"count": len(str(prompt)), "error_code": 0}

    def get_payload(self, prompts: str, stream=True):
        self.payload['stream'] = stream
        messages = [{"sender_type": "USER", "sender_name": "小明", "text": prompts}]
        self.payload['messages'] = messages
        return self.payload

    def generate_stream_gate(self, params: Dict):
        self.call_ct += 1
        try:
            text = ''
            res = requests.post(self.url, headers=self.headers,
                                json=self.get_payload(params.get('prompt')), stream=True)
            for chunk in res.iter_lines():
                data = chunk.decode().split(':', 1)
                if len(data) == 2:
                    out = json.loads(data[1])
                    reply = out['reply']
                    if reply:
                        yield json.dumps({"error_code": 0, "text": reply, "finish_reason": "stop"}).encode() + b'\0'
                    else:
                        text += out['choices'][0]['messages'][0]['text']
                        yield json.dumps({"error_code": 0, "text": text, "finish_reason": None}).encode() + b'\0'
        except Exception as e:
            yield json.dumps({"error_code": 500, "text": e.str()}).encode() + b'\0'

    def generate_gate(self, params):
        self.call_ct += 1

        try:
            res = requests.post(self.url, headers=self.headers,
                                json=self.get_payload(params.get('prompt'), stream=False), stream=True)
            return {"error_code": 0, "text": res.json()['reply'], "finish_reason": "stop"}
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

    worker = MiniMaxWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21002",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    uvicorn.run(app, port=21002)
