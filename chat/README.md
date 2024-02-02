# local model config

## setup a control

```shell
python -m fastchat.serve.controller --port 20001
```

## setup a model worker

```shell
python -m fastchat.serve.model_worker --port 21005 \
    --worker-address http://127.0.0.1:21005 \
    --controller-address http://127.0.0.1:20001 \
    --model-name chatglm2-6b --model-path THUDM/chatglm2-6b
```

## setup openai server

```shell
python -m fastchat.serve.openai_api_server --port 20000 --controller-address http://127.0.0.1:20001
```
