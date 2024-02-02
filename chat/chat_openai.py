from typing import List, Dict
from common import Chat
from openai import OpenAI
import streamlit as st
from streamlit_chatbox import ChatBox
import os


class OpenaiChat(Chat):
    def __init__(self, **kargs):
        super().__init__(name='openai')
        if key := st.session_state.get('openai_key'):
            os.environ.setdefault('OPENAI_API_KEY', key)
        if not os.environ.get('OPENAI_API_KEY'):
            openai_key = st.text_input("请输入openai的api key")
            if st.button('确定'):
                st.session_state['openai_key'] = openai_key
                os.environ.setdefault('OPENAI_API_KEY', openai_key)
                st.rerun()
            st.stop()
        self.client = OpenAI()
        self.model_name = 'gpt-3.5-turbo'
        self.have_tokens = False

    def request(self, messages: List[Dict], stream=True, chatbox: ChatBox = ChatBox()):
        self.messages = messages
        chatbox.ai_say('正在思考...')
        self.res = self.client.chat.completions.create(
             model=self.model_name, messages=messages, stream=True
        )

    def response(self, chatbox: ChatBox):
        self.content = ''
        for chunk in self.res:
            if chunk.choices[0].delta.content:
                self.content += chunk.choices[0].delta.content
                chatbox.update_msg(self.content)
            else:
                chatbox.update_msg(self.content, streaming=False)
