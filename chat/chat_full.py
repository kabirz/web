import streamlit as st
from streamlit_chatbox import ChatBox
from dotenv import load_dotenv
from datetime import datetime
import os

PATH = __file__.rsplit('/', 1)[0]
AI = f'{PATH}/img/AI.jpg'
USER = f'{PATH}/img/USER.png'
st.set_page_config('ChatBot Online', AI)
load_dotenv(os.path.expanduser('~/.env'))

chatbox = ChatBox(assistant_avatar=AI, user_avatar=USER)
MODELS = ['智谱', '讯飞', 'OpenAI']
with st.sidebar:
    model_name = st.radio('请选择大模型', MODELS, horizontal=True)
if model_name == '智谱':
    from chat_zhipu import ZhipuChat
    chat = ZhipuChat()
elif model_name == '讯飞':
    from chat_sk import SkChat
    chat = SkChat()
elif model_name == 'OpenAI':
    from chat_openai import OpenaiChat
    chat = OpenaiChat()

with st.sidebar:
    temperature = st.slider("Temperature：", 0.0, 1.0, 0.5, 0.05)
    history_len = st.number_input("历史对话轮数：", 0, 20, 4)
    token = st.empty()
chat.show_tokens(token)
chatbox.use_chat_name(chat.model)
st.markdown(f'我是{model_name}大语言模型，您有任何问题都可以问我。')
chatbox.output_messages()
if prompt := st.chat_input("请输入您要问的问题"):
    if prompt == '/clear':
        chatbox.reset_history(name=chat.model)
        st.rerun()
    messages = []
    chatbox.user_say(prompt)
    for his in chatbox.history[-history_len*2:]:
        messages.append({'role': his['role'], 'content': his['elements'][0].content})
    chat.request(temperature, messages=messages, chatbox=chatbox)
    chat.response(chatbox)
    chat.show_tokens(token)

with st.sidebar:
    export_btn = st.download_button(
        '导出聊天记录',
        ''.join(chatbox.export2md(user_bg_color='#EFEFEF', ai_bg_color='#CFCFCF')),
        file_name=f'{chat.model}_{datetime.now():%Y-%m-%d %H.%M}_对话记录.md',
        mime='text/markdown',
        use_container_width=True,
    )
