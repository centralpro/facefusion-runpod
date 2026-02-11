#!/usr/bin/env python3
"""
RunPod Hub 需要的入口文件。
Load Balancer 模式：启动 serverless_app.py（FastAPI + Gradio + /ping）
"""
import os
import sys

# 切换到 facefusion 目录并启动 serverless_app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'facefusion'))
os.chdir(os.path.join(os.path.dirname(__file__), 'facefusion'))

import serverless_app  # 执行 uvicorn 启动