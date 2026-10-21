# Runner image for scripts/run_all.py: Python 3.12 + Node 24 on a CUDA base, so the run can see the host's NVIDIA GPU
# (docker run --gpus all). The exercises themselves are CPU-only and offline; the GPU is reported, not required.
FROM node:24-bookworm-slim AS node

FROM nvidia/cuda:12.6.3-base-ubuntu24.04
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt
WORKDIR /work
