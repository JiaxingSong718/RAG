import os
from huggingface_hub import snapshot_download


snapshot_download(
  repo_id="shibing624/text2vec-base-chinese",
  local_dir="./EmbeddingModel",
  cache_dir="./EmbeddingModel"
)