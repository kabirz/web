import streamlit as st
from streamlit_chatbox import ChatBox
from zhipuai import ZhipuAI
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config('AI聊天室', '🤖')
model = 'glm-4'
history_len = 4
client = ZhipuAI(api_key=os.environ.get('ZHIPU_API_KEY', ''))
st.session_state.setdefault('tokens', {'pts': 0, 'cts': 0, 'tts': 0})


with st.sidebar:
    with st.container():
        st.markdown('''**Tokens**:
|   promts | completions | totals |
|    ----  |     ----    | ----   |
|    {pts} |     {cts}   |  {tts} |
'''.format(**st.session_state['tokens']))

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
        if chunk.usage:
            st.session_state['tokens']['pts'] += chunk.usage.prompt_tokens
            st.session_state['tokens']['cts'] += chunk.usage.completion_tokens
            st.session_state['tokens']['tts'] += chunk.usage.total_tokens
        chatbox.update_msg(text)
    chatbox.update_msg(text, streaming=False)
