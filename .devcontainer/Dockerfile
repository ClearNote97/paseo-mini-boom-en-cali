# This Dockerfile is used for the development container in VS Code Remote Containers.
# It sets up a Python environment with the necessary tools for development.
FROM python:3.14.5-slim-bookworm

# Set the working directory in the container
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages and clean up apt cache to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv, a Python package manager, to manage dependencies in the development environment
COPY --from=ghcr.io/astral-sh/uv:0.11.13 /uv /uvx /bin/