# FaceFusion on RunPod with UI (Gradio)
# 支持通过 RunPod 暴露的端口访问 Web UI

FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 安装 Python 3.10+、ffmpeg、curl（facefusion 依赖）
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-pip \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /app

# 复制 facefusion 子项目
COPY facefusion/ /app/facefusion/

# 安装依赖：使用 onnxruntime-gpu 以支持 CUDA
RUN python -m pip install --no-cache-dir -r /app/facefusion/requirements.txt && \
    python -m pip uninstall -y onnxruntime 2>/dev/null || true && \
    python -m pip install --no-cache-dir onnxruntime-gpu==1.24.1

# RunPod 通过端口 8000 暴露 HTTP，Gradio 监听 0.0.0.0
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=8000

EXPOSE 8000

WORKDIR /app/facefusion

# 启动 FaceFusion UI（run 命令启动 Gradio）
CMD ["python", "facefusion.py", "run", "--execution-providers", "cuda"]
