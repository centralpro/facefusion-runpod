# FaceFusion on RunPod

将仓库内 `facefusion` 部署到 RunPod，支持通过 **Web UI（Gradio）** 在浏览器中访问和使用。

## 前置要求

- RunPod 账号
- 本地已安装 Docker（用于构建镜像）

## 部署步骤

### 1. 构建 Docker 镜像

在项目根目录执行：

```bash
docker build -t facefusion-runpod:latest .
```

### 2. 推送到镜像仓库

RunPod 支持从 Docker Hub 或私有仓库拉取镜像。

**Docker Hub 示例：**

```bash
docker tag facefusion-runpod:latest <你的用户名>/facefusion-runpod:latest
docker push <你的用户名>/facefusion-runpod:latest
```

### 3. 在 RunPod 创建 Pod

1. 登录 [RunPod](https://www.runpod.io/) → **Pods** → **Deploy**。
2. 选择 **GPU** 机型（建议至少 1 张 GPU，如 RTX 4090 / A100）。
3. **Container Image** 填：`<你的用户名>/facefusion-runpod:latest`（或你的镜像地址）。
4. **Container Disk** 建议 ≥ 20 GB（用于模型与临时文件）。
5. **Expose HTTP Ports**：填 **8000**（与镜像内 `GRADIO_SERVER_PORT=8000` 一致）。
6. 如需挂载存储或设置环境变量，在高级选项中配置。
7. 创建并启动 Pod。

### 4. 通过 UI 访问

Pod 运行后：

1. 在 RunPod 控制台找到该 Pod 的 **Connect** 或 **HTTP Service**。
2. 使用 RunPod 提供的 **端口 8000 的 URL**（例如 `https://xxx-8000.proxy.runpod.net`）在浏览器中打开。
3. 即可使用 FaceFusion 的 Gradio Web 界面。

## 环境变量（可选）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `GRADIO_SERVER_NAME` | 监听地址，RunPod 需对外暴露时设为 `0.0.0.0` | `0.0.0.0`（镜像内已设） |
| `GRADIO_SERVER_PORT` | Gradio 监听端口 | `8000` |
| `RUNPOD_POD_PORT` | RunPod 暴露的端口，若不设 `GRADIO_SERVER_PORT` 会优先用此端口 | - |

在 RunPod Pod 的 **Template** 或 **Override** 中可覆盖上述变量。

## 本地用 Docker 测试

```bash
docker build -t facefusion-runpod:latest .
docker run --gpus all -p 8000:8000 facefusion-runpod:latest
```

浏览器访问：`http://localhost:8000`。

---

## Serverless 部署（按使用付费）

若希望 **仅在有访问时计费**，可使用 RunPod **Serverless + Load Balancer**，Worker 在有请求时启动、空闲一段时间后缩容，按 GPU 使用时长计费。

### 1. 构建 Serverless 镜像

在项目根目录执行：

```bash
docker build -f Dockerfile.serverless -t facefusion-runpod-serverless:latest .
```

### 2. 推送到镜像仓库

```bash
docker tag facefusion-runpod-serverless:latest <你的用户名>/facefusion-runpod-serverless:latest
docker push <你的用户名>/facefusion-runpod-serverless:latest
```

### 3. 在 RunPod 创建 Serverless Endpoint

1. 登录 [RunPod](https://www.runpod.io/) → **Serverless** → **New Endpoint**。
2. **Import from Docker Registry**，镜像填：`<你的用户名>/facefusion-runpod-serverless:latest`。
3. **Endpoint Type** 选择 **Load Balancer**（不要选 Queue-based）。
4. **GPU Configuration** 选择至少一张 GPU（如 24GB）。
5. **重要**：将 **Max workers** 设为 **1**（避免上传/会话被分散到不同 Worker，导致 404/403）。
6. 其他保持默认，**Deploy Endpoint**。

### 4. 通过 UI 访问

- 创建完成后，RunPod 会给出 Endpoint URL，形如：`https://<ENDPOINT_ID>.api.runpod.ai`。
- **需携带 API Key**：浏览器访问需添加 `Authorization: Bearer <API_KEY>` 头，可用 [ModHeader](https://modheader.com/) 等扩展，或将 key 放在 URL：`https://<ENDPOINT_ID>.api.runpod.ai/?api_key=<你的API_KEY>`。
- 首次访问或冷启动时 Worker 会拉取镜像并启动，可能需要几十秒；之后一段时间内有流量会保持 warm，无流量后会自动缩容，仅按实际使用计费。

### 5. 可选：挂载 Network Volume 持久化上传

- 在 Endpoint 设置中挂载 Network Volume 到 **`/data`**。
- 上传文件会存储在 `/data/facefusion/gradio`，Worker 重启后仍可保留。

### 健康检查说明

Serverless 镜像内已提供 **`/ping`** 接口（返回 `{"status":"healthy"}`），供 RunPod Load Balancer 做健康检查，无需额外配置。

---

## 项目结构说明

- **facefusion/**：FaceFusion 主项目（含 Gradio UI）。
- **Dockerfile**：Pod 部署用，基于 CUDA 12.2，启动 `facefusion run`。
- **Dockerfile.serverless**：Serverless Load Balancer 用，启动 `serverless_app.py`（FastAPI + /ping + Gradio）。
- **facefusion/serverless_app.py**：Serverless 入口，挂载 Gradio 并暴露 `/ping`。
- **run.sh**：可选启动脚本（Pod 用）。

Gradio 的 `server_name` / `server_port` 由 `facefusion/facefusion/uis/core.py` 的 `get_launch_options()` 根据环境变量设置；Serverless 模式下由 FastAPI + Uvicorn 监听 `PORT`（默认 80）。
