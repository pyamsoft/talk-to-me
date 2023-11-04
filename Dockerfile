FROM python:3.10-slim

WORKDIR /talk-to-me

# Open up
RUN umask 0022

# Install deps
RUN apt -y update && apt -y upgrade && apt -y install curl build-essential llvm ffmpeg

# Install poetry
RUN curl -sSL 'https://install.python-poetry.org' | python3 -

# Install voice model
RUN curl -s 'https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx' -o en_US-lessac-medium.onnx
RUN curl -s 'https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json' -o en_US-lessac-medium.onnx.json

# Copy source
COPY main.py ./
COPY pyproject.toml ./
COPY README.md ./
COPY LICENSE ./
COPY talktome ./talktome
COPY bin/runner /root/.local/bin/runner

# Run the main file in the virtualenv
# Run the installer like this in the entrypoint to avoid the actual image being too large
ENTRYPOINT [ "/root/.local/bin/runner" ]
