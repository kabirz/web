from abc import ABC, abstractmethod
from typing import List, Dict
from streamlit_chatbox import ChatBox
import streamlit as st

TOKENS = '''**Tokens**:
| prompts | completions | totals |
|   ----  |     ----    |  ----  |
|   {pts} |     {cts}   |  {tts} |
'''


class Chat(ABC):
    def __init__(self, name, **kargs):
        st.session_state.setdefault(f'{name}_tokens', {'pts': 0, 'cts': 0, 'tts': 0})
        self.tokens = {'pts': 0, 'cts': 0, 'tts': 0}
        self.model_name = 'default'
        self.have_tokens = True
        self.name = name

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
        st.session_state[f'{self.name}_tokens']['pts'] += self.tokens['pts']
        st.session_state[f'{self.name}_tokens']['cts'] += self.tokens['cts']
        st.session_state[f'{self.name}_tokens']['tts'] += self.tokens['tts']
        return st.session_state[f'{self.name}_tokens']

    def show_tokens(self, id: st = st.empty()):
        if self.have_tokens:
            id.markdown(TOKENS.format(**self._get_tokens()))

    def __exit__(self):
        pass
