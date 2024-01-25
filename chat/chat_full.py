import streamlit as st
from streamlit_chatbox import ChatBox, Image
import zhipuai

st.set_page_config('AI聊天室', '🤖')

history_len = 4
if not st.session_state.get('zhipu_key'):
    zhipu_key = st.text_input("请输入智谱的api key")
    if st.button('确定'):
        st.session_state['zhipu_key'] = zhipu_key
        st.rerun()
    st.stop()

st.session_state.setdefault('tokens', {'pts': 0, 'cts': 0, 'tts': 0})


def show_tokens(id: st = st.empty()):
    return id.markdown('''**Tokens**:
| prompts | completions | totals |
|   ----  |     ----    |  ----  |
|   {pts} |     {cts}   |  {tts} |
'''.format(**st.session_state['tokens']))


chatbox = ChatBox(assistant_avatar='🤖', user_avatar='🏆')
with st.sidebar:
    model = st.selectbox('请选择模型', ['glm-4', 'glm-3-turbo', '绘画'])
    history_len = st.number_input("历史对话轮数：", 0, 20, 4)
    chatbox.use_chat_name(model)
    if model != '绘画':
        with st.container():
            token = st.empty()
            token = show_tokens(token)

st.markdown('我是智谱大语言模型，您有任何问题都可以问我。')
chatbox.output_messages()

if prompt := st.chat_input("请输入您要问的问题"):
    client = zhipuai.ZhipuAI(api_key=st.session_state.get('zhipu_key'))
    messages = []
    chatbox.user_say(prompt)
    if model in ('glm-4', 'glm-3-turbo'):
        for his in chatbox.history[-history_len*2:]:
            messages.append({'role': his['role'], 'content': his['elements'][0].content})
        chatbox.ai_say('正在思考...')
        response = client.chat.completions.create(model=model, messages=messages, stream=True)
        text = ''
        for chunk in response:
            text += chunk.choices[0].delta.content
            if chunk.usage:
                st.session_state['tokens']['pts'] += chunk.usage.prompt_tokens
                st.session_state['tokens']['cts'] += chunk.usage.completion_tokens
                st.session_state['tokens']['tts'] += chunk.usage.total_tokens
                show_tokens(token)
            chatbox.update_msg(text)
        chatbox.update_msg(text, streaming=False)
    elif model == '绘画':
        chatbox.ai_say('正在绘画中...')
        try:
            response = client.images.generations(model='cogview-3', prompt=prompt)
            if response.data:
                chatbox.update_msg(Image(response.data[0].url), streaming=False)
            else:
                chatbox.update_msg('绘画生成失败', streaming=False)
        except zhipuai.core._errors.APIRequestFailedError as e:
            out = eval(e.response.text)
            chatbox.update_msg(out['error']['message'], streaming=False)
