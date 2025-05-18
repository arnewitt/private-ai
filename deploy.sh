#!/usr/bin/env bash

set -e

declare -A SERVICES=(
  ["litellm"]="config/litellm/docker-compose.yaml"
  ["langfuse"]="config/langfuse/docker-compose.yaml"
  #["ollama"]="config/ollama/docker-compose.yaml"
  #["openwebui"]="config/openwebui/docker-compose.yaml"
  #["gradio"]="config/gradio/docker-compose.yaml"
)

echo "Select services to deploy independently:"
for SERVICE in $(printf "%s\n" "${!SERVICES[@]}" | sort); do
  read -p "Include $SERVICE? (y/n): " yn
  if [[ "$yn" =~ ^[Yy]$ ]]; then
    echo "➡️  Deploying $SERVICE..."
    docker compose -f "${SERVICES[$SERVICE]}" -p "$SERVICE" up -d --build --remove-orphans
  fi
done

echo
echo "✅ All selected services deployed independently."