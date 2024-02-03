from common import Chat
from typing import List, Dict
import streamlit as st
from streamlit_chatbox import ChatBox
import requests
import json


class LocalChat(Chat):
    def __init__(self, **kargs):
        super().__init__(name='local')
        self.have_tokens = False
        with st.sidebar:
            self.host = st.text_input("请输入host地址:", value='127.0.0.1:20000')

        try:
            data = requests.get(f'http://{self.host}/v1/models')
            self.models = [i['id'] for i in data.json().get('data')]
        except Exception:
            st.error('输入的host地址或者端口错误')
            st.stop()
        with st.sidebar:
            self.model_name = st.selectbox("选择模型", self.models)

    def request(self, temperature: float, messages: List[Dict], stream=True, chatbox: ChatBox = ChatBox()):
        self.messages = messages
        data = {
            'model': self.model_name,
            'stream': True,
            'messages': messages,
            'temperature': temperature,
        }
        try:
            self.res = requests.post(f'http://{self.host}/v1/chat/completions', json=data, stream=True)
            chatbox.ai_say('正在思考...')
        except requests.exceptions.ConnectionError:
            st.error("连接拒绝, 请确认host地址或者端口是否正常")
            st.stop()

    def response(self, chatbox: ChatBox):
        self.content = ''
        for chunk in self.res.iter_lines():
            if not chunk:
                continue
            data = chunk.decode().split(':', 1)
            try:
                data_json = json.loads(data[1])
                self.content += data_json['choices'][0]['delta']['content']
                chatbox.update_msg(self.content)
            except KeyError:
                pass
            except json.decoder.JSONDecodeError:
                chatbox.update_msg(self.content, streaming=False)
