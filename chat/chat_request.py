import requests
import streamlit as st
from streamlit_chatbox import ChatBox
import json
import time
import jwt

st.set_page_config('AI聊天室', '🤖')


def generate_token(apikey: str, exp_seconds: int):
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)

    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }

    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )


def show_tokens(id: st = st.empty()):
    return id.markdown('''**Tokens**:
| prompts | completions | totals |
|   ----  |     ----    |  ----  |
|   {pts} |     {cts}   |  {tts} |
'''.format(**st.session_state['tokens']))


if not st.session_state.get('zhipu_key'):
    zhipu_key = st.text_input("请输入智谱的api key")
    if st.button('确定'):
        st.session_state['zhipu_key'] = zhipu_key
        st.rerun()
    st.stop()

history_len = 4
st.session_state.setdefault('tokens', {'pts': 0, 'cts': 0, 'tts': 0})
chatbox = ChatBox(assistant_avatar='🤖', user_avatar='🏆')
with st.sidebar:
    model = st.selectbox('请选择模型', ['glm-4', 'glm-3-turbo'])
    history_len = st.number_input("历史对话轮数：", 0, 20, 4)
    chatbox.use_chat_name(model)
    with st.container():
        token = st.empty()
        token = show_tokens(token)

st.markdown('我是智谱大语言模型，您有任何问题都可以问我。')
chatbox.output_messages()
history_len = 4
url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": generate_token(st.session_state['zhipu_key'], 120)
}
messages = []

if prompt := st.chat_input('请输入您要问的问题'):
    chatbox.user_say(prompt)
    for his in chatbox.history[-history_len*2:]:
        messages.append({'role': his['role'], 'content': his['elements'][0].content})
    data = {'model': 'glm-4', 'messages': messages, 'stream': True}
    chatbox.ai_say('正在思考...')
    response = requests.post(url, json=data, headers=headers, stream=True)
    text = ''
    for chunk in response.iter_lines():
        data_str = chunk.decode()
        if len(data_str) > 20:
            data_dict = json.loads(data_str[6:])
            buf = data_dict['choices'][0]['delta']['content']
            text += buf
            if data_dict.get('usage'):
                usage = data_dict.get('usage')
                st.session_state['tokens']['pts'] += usage['prompt_tokens']
                st.session_state['tokens']['cts'] += usage['completion_tokens']
                st.session_state['tokens']['tts'] += usage['total_tokens']
                show_tokens(token)
                chatbox.update_msg(text, streaming=False)
            else:
                chatbox.update_msg(text)
