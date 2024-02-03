from common import Chat
from typing import List, Dict
import streamlit as st
from streamlit_chatbox import ChatBox
import requests
import json
import os


class OpenaiChat(Chat):
    def __init__(self, **kargs):
        super().__init__(name='local')
        self.have_tokens = False
        with st.sidebar:
            self.local = st.toggle("使用本地模型")
        if not self.local:
            if key := st.session_state.get('openai_key'):
                os.environ.setdefault('OPENAI_API_KEY', key)
            if not os.environ.get('OPENAI_API_KEY'):
                openai_key = st.text_input("请输入openai的api key")
                if st.button('确定'):
                    st.session_state['openai_key'] = openai_key
                    os.environ.setdefault('OPENAI_API_KEY', openai_key)
                    st.rerun()
                st.stop()
            self.host = 'https://api.openai.com'
            self.headers = {'Authorization': 'Bearer {}'.format(os.environ.get('OPENAI_API_KEY'))}
            self.model_name = 'gpt-3.5-turbo'
        else:
            with st.sidebar:
                self.host = st.text_input("请输入host地址:", value='http://127.0.0.1:20000')
            self.headers = dict()

            try:
                data = requests.get(f'{self.host}/v1/models')
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
            self.res = requests.post(f'{self.host}/v1/chat/completions', json=data, stream=True, headers=self.headers)
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
