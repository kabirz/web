from common import Chat
import hmac
import hashlib
import base64
import json
import ssl
from typing import List, Dict
from datetime import datetime
import websocket
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import streamlit as st
from streamlit_chatbox import ChatBox
import os


class SkChat(Chat):
    MODELS = {'v3.5': 'generalv3.5', 'v3.1': 'generalv3', 'v2.1': 'generalv2', 'v1.1': 'general'}
    KEYS = ['SK_APPID', 'SK_APPKey', 'SK_APPSecret']

    def __init__(self, **kargs):
        super().__init__(name='sk')
        keys = []
        for key in self.KEYS:
            if st.session_state.get(key):
                os.environ.setdefault(key, st.session_state.get(key))
            if not os.environ.get(key):
                value = st.text_input(f"请输入讯飞的{key}")
                keys.append((key, value))
        self.appid, self.appkey, self.appsecret = map(lambda x: os.environ.get(x), self.KEYS)
        if not all([self.appid, self.appkey, self.appsecret]):
            if st.button('确定'):
                for k, v in keys:
                    st.session_state[k] = v
                os.environ.setdefault(k, v)
                st.rerun()
            st.stop()
        with st.sidebar:
            self.model_name = st.selectbox('请选择类别', self.MODELS.keys())
        st.session_state.setdefault('sk_url', self._get_url())

    def _get_url(self, host='spark-api.xf-yun.com', version='v3.5'):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        path = f'/{version}/chat'
        signature_origin = "host: " + host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + path + " HTTP/1.1"

        signature_sha = hmac.new(self.appsecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = f'api_key="{self.appkey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": host
        }
        url = f"wss://{host}{path}" + '?' + urlencode(v)
        return url

    def _message_handler(self, message):
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            return False, ""
        else:
            choices = data['payload']['choices']
            status = choices['status']
            content = choices['text'][0]['content']
            if status == 2:
                tokens = data['payload']['usage']['text']
                self.prompt_tokens = tokens['prompt_tokens']
                self.completion_tokens = tokens['completion_tokens']
                self.total_tokens = tokens['total_tokens']
            return status == 2, content

    def _gen_params(self):
        data = {
            "header": {"app_id": self.appid, "uid": "1234"},
            "parameter": {
                "chat": {
                    "domain": self.MODELS[self.model_name],
                    "temperature": 0.5,
                    "max_tokens": 2048
                }
            },
            "payload": {"message": {"text": self.messages}}
        }
        return data

    def request(self, messages: List[Dict], stream=True, chatbox: ChatBox = ChatBox()):
        self.messages = messages
        chatbox.ai_say('正在思考...')
        self.client = websocket.create_connection(st.session_state.get('sk_url'), sslopt={"cert_reqs": ssl.CERT_NONE})
        self.messages = messages
        self.client.send(json.dumps(self._gen_params()))

    def response(self, chatbox: ChatBox):
        finish = False
        self.content = ''
        while not finish:
            output = self.client.recv()
            finish, data = self._message_handler(output)
            self.content += data
            chatbox.update_msg(self.content, streaming=not finish)

    def __exit__(self):
        self.client.close()
