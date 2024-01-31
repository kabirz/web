from typing import List, Dict
from common import Chat
import zhipuai
from zhipuai import ZhipuAI
import streamlit as st
from streamlit_chatbox import ChatBox, Image
import os


class ZhipuChat(Chat):
    MODELS = ['glm-4', 'glm-3-turbo', '绘画']

    def __init__(self, **kargs):
        super().__init__(name='zhipu')
        if key := st.session_state.get('zhipu_key'):
            os.environ.setdefault('ZHIPUAI_API_KEY', key)
        if not os.environ.get('ZHIPUAI_API_KEY'):
            zhipu_key = st.text_input("请输入智谱的api key")
            if st.button('确定'):
                st.session_state['zhipu_key'] = zhipu_key
                os.environ.setdefault('ZHIPUAI_API_KEY', zhipu_key)
                st.rerun()
            st.stop()
        self.client = ZhipuAI()
        with st.sidebar:
            self.model_name = st.selectbox('请选择类别', self.MODELS)

    @property
    def model(self):
        return f'zhipu_{self.model_name}'

    def request(self, messages: List[Dict], stream=True, chatbox: ChatBox = ChatBox()):
        if self.model_name == "绘画":
            chatbox.ai_say('正在绘画中...')
            try:
                prompt = messages[-1]['content']
                self.res = self.client.images.generations(model='cogview-3', prompt=prompt)
                if self.res.data:
                    self.out = Image(self.res.data[0].url)
                else:
                    self.out = '绘画生成失败'
            except zhipuai.APIRequestFailedError as e:
                out = eval(e.response.text)
                self.out = out['error']['message']
        else:
            chatbox.ai_say('正在思考...')
            self.res = self.client.chat.completions.create(
             model=self.model_name, messages=messages, stream=True
            )

    def response(self, chatbox: ChatBox):
        if self.model_name == "绘画":
            chatbox.update_msg(self.out, streaming=False)
            return
        text = ''
        for chunk in self.res:
            text += chunk.choices[0].delta.content
            if chunk.usage:
                self.tokens['pts'] = chunk.usage.prompt_tokens
                self.tokens['cts'] = chunk.usage.completion_tokens
                self.tokens['tts'] = chunk.usage.total_tokens
                chatbox.update_msg(text, streaming=False)
            else:
                chatbox.update_msg(text)
