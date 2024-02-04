# local model config

## setup a control

```shell
python -m fastchat.serve.controller --port 20001
```

## setup a model worker

```shell
python zhipu.py
```

## setup openai server

```shell
python -m fastchat.serve.openai_api_server --port 20000 --controller-address http://127.0.0.1:20001
```
