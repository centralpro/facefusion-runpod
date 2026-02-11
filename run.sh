#!/bin/bash
# RunPod 启动脚本：启动 FaceFusion Web UI，供外部通过端口访问

export GRADIO_SERVER_NAME="${GRADIO_SERVER_NAME:-0.0.0.0}"
export GRADIO_SERVER_PORT="${GRADIO_SERVER_PORT:-${RUNPOD_POD_PORT:-8000}}"

cd /app/facefusion
exec python facefusion.py run --execution-providers cuda
