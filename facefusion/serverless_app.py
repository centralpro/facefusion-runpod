#!/usr/bin/env python3
"""
RunPod Serverless Load Balancer 入口。
启动 Gradio UI，并暴露 /ping 健康检查供 RunPod 使用。
仅在有请求时计费（按 GPU 使用时长）。
"""
import os
import sys

# 临时目录：支持挂载 Network Volume 到 /data 持久化上传
temp_path = os.environ.get("TEMP_PATH") or (
    os.path.dirname(os.environ["GRADIO_TEMP_DIR"])
    if os.environ.get("GRADIO_TEMP_DIR")
    else "/data/facefusion"
)
try:
    os.makedirs(temp_path, exist_ok=True)
    os.makedirs(os.path.join(temp_path, "gradio"), exist_ok=True)
except OSError:
    temp_path = "/tmp/facefusion"
    os.makedirs(temp_path, exist_ok=True)

# 以 serverless 子命令运行，只构建 UI 不直接 launch
sys.argv = [
    "facefusion.py",
    "serverless",
    "--execution-providers", "cuda",
    "--temp-path", temp_path,
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
