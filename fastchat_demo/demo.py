from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    streaming=False,
    openai_api_key="EMPTY",
    openai_api_base="http://localhost:20000/v1",
    model_name='chatGLM-130B',
    temperature=0.7,
    max_tokens=10,
)

out = model.invoke("你好")
print(out.content)
