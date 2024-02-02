from abc import ABC, abstractmethod
from typing import List, Dict
from streamlit_chatbox import ChatBox
import streamlit as st
import tokens_count

TOKENS = '''**Tokens**:
| prompts | completions | totals |
|   ----  |     ----    |  ----  |
|   {pts} |     {cts}   |  {tts} |
'''


class Chat(ABC):
    def __init__(self, name, **kargs):
        st.session_state.setdefault(f'{name}_tokens', {'pts': 0, 'cts': 0, 'tts': 0})
        self.model_name = 'default'
        self.have_tokens = True
        self.name = name
        self.messages = None
        self.content = None
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
        self.s_tokens = st.session_state[f'{self.name}_tokens']

    @abstractmethod
    def request(self, messages: List[Dict], stream=True, chatbox: ChatBox = ChatBox()):
        ...

    @abstractmethod
    def response(self, chatbox: ChatBox):
        ...

    @property
    def model(self):
        return f'{self.name}_{self.model_name}'

    def _get_tokens(self) -> Dict:
        if not self.have_tokens and self.content:
            self.prompt_tokens = tokens_count.num_tokens_from_messages(self.messages)
            self.completion_tokens = tokens_count.num_tokens_from_string(self.content)
            self.total_tokens = self.prompt_tokens + self.completion_tokens

        self.s_tokens['pts'] += self.prompt_tokens
        self.s_tokens['cts'] += self.completion_tokens
        self.s_tokens['tts'] += self.total_tokens

        return self.s_tokens

    def show_tokens(self, id: st = st.empty()):
        id.markdown(TOKENS.format(**self._get_tokens()))

    def __exit__(self):
        pass
