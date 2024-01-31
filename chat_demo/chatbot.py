import streamlit as st
from streamlit_chatbox import ChatBox
from zhipuai import ZhipuAI
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config('AI聊天室', '🤖', layout='wide')
model = 'glm-4'
history_len = 4
client = ZhipuAI(api_key=os.environ.get('ZHIPU_API_KEY', ''))

chatbox = ChatBox(assistant_avatar='🤖', user_avatar='🏆', greetings=['我是智谱大模型', '您有任何问题都可以问我'])
chatbox.output_messages()

if prompt := st.chat_input("请输入您要问的问题"):
    messages = []
    chatbox.user_say(prompt)
    for his in chatbox.history[-history_len:]:
        messages.append({'role': his['role'], 'content': his['elements'][0].content})
    response = client.chat.completions.create(model=model, messages=messages, stream=True)
    text = ''
    chatbox.ai_say(text)
    for chunk in response:
        text += chunk.choices[0].delta.content
        chatbox.update_msg(text)
    chatbox.update_msg(text, streaming=False)
