import streamlit as st
from streamlit_chatbox import ChatBox
from dotenv import load_dotenv

st.set_page_config('AI聊天室', '🤖')
load_dotenv()

chatbox = ChatBox(assistant_avatar='🤖', user_avatar='🏆')
with st.sidebar:
    model_name = st.radio('请选择大模型', ['智谱', '讯飞星火'], horizontal=True)
if model_name == '智谱':
    from chat_zhipu import ZhipuChat
    chat = ZhipuChat()
elif model_name == '讯飞星火':
    from chat_sk import SkChat
    chat = SkChat()
else:
    st.rerun()

with st.sidebar:
    history_len = st.number_input("历史对话轮数：", 0, 20, 4)
    token = st.empty()
chat.show_tokens(token)
chatbox.use_chat_name(chat.model)
st.markdown(f'我是{model_name}大语言模型，您有任何问题都可以问我。')
chatbox.output_messages()
if prompt := st.chat_input("请输入您要问的问题"):
    messages = []
    chatbox.user_say(prompt)
    for his in chatbox.history[-history_len*2:]:
        messages.append({'role': his['role'], 'content': his['elements'][0].content})
    chat.request(messages=messages, chatbox=chatbox)
    chat.response(chatbox)
    chat.show_tokens(token)
