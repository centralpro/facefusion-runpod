#!/usr/bin/env python3
"""
RunPod Serverless Load Balancer 入口。
启动 Gradio UI，并暴露 /ping 健康检查供 RunPod 使用。
仅在有请求时计费（按 GPU 使用时长）。
"""
import os
import sys

# 以 serverless 子命令运行，只构建 UI 不直接 launch
sys.argv = [
    "facefusion.py",
    "serverless",
    "--execution-providers", "cuda",
]

from facefusion import core

blocks = core.cli()
if blocks is None:
    sys.exit(2)

from fastapi import FastAPI
import gradio as gr

app = FastAPI()


@app.get("/ping")
def ping():
    """RunPod Load Balancer 健康检查（必须）"""
    return {"status": "healthy"}


app = gr.mount_gradio_app(app, blocks, path="/")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 80))
    uvicorn.run(app, host="0.0.0.0", port=port)
