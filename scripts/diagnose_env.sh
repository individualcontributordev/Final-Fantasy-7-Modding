#!/usr/bin/env bash
# Diagnostic script: gathers workstation/env info relevant to train_ff7.py /
# run_ff7_agent.py troubleshooting. Read-only, no secrets printed.
set -uo pipefail

echo "===== OS / SHELL ====="
uname -a
echo "SHELL=$SHELL"
echo

echo "===== CONDA ====="
if command -v conda >/dev/null 2>&1; then
    conda --version
    echo "--- envs ---"
    conda env list
    echo "--- active env ---"
    echo "CONDA_DEFAULT_ENV=${CONDA_DEFAULT_ENV:-<none>}"
else
    echo "conda not found on PATH"
fi
echo

echo "===== PYTHON (current shell) ====="
which python3 2>/dev/null || echo "python3 not found"
python3 --version 2>&1
echo

echo "===== PYTHON (inside ff7_train env, if conda available) ====="
if command -v conda >/dev/null 2>&1; then
    conda run -n ff7_train python3 --version 2>&1
    conda run -n ff7_train python3 -c "import sys; print('exe:', sys.executable)" 2>&1
fi
echo

echo "===== KEY PACKAGE VERSIONS (current python3) ====="
python3 - <<'EOF'
mods = ["torch", "unsloth", "unsloth_zoo", "trl", "transformers", "peft",
        "bitsandbytes", "accelerate", "datasets", "torchao", "triton"]
for m in mods:
    try:
        mod = __import__(m)
        print(f"{m}: {getattr(mod, '__version__', 'unknown')}")
    except Exception as e:
        print(f"{m}: NOT INSTALLED ({e.__class__.__name__})")
EOF
echo

echo "===== CUDA / TORCH RUNTIME CHECK ====="
python3 - <<'EOF'
try:
    import torch
    print("torch.__version__:", torch.__version__)
    print("torch.cuda.is_available():", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("device name:", torch.cuda.get_device_name(0))
        free, total = torch.cuda.mem_get_info(0)
        print(f"free/total VRAM: {free/1e9:.2f} GB / {total/1e9:.2f} GB")
except Exception as e:
    print("torch check failed:", e)
EOF
echo

echo "===== NVIDIA-SMI ====="
if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,driver_version --format=csv
else
    echo "nvidia-smi not found on PATH"
fi
echo

echo "===== ENV VARS (names only, no values, filtered for relevance) ====="
env | grep -Eo '^(HF_|CUDA_|UNSLOTH_|TORCH_|TRITON_)[A-Z_]*' | sort -u
echo

echo "===== WORKSPACE FILE CHECK ====="
cd "$(dirname "$0")/.." || exit 1
pwd
ls -la train_ff7.py run_ff7_agent.py .env 2>&1
echo "--- dataset ---"
ls -la data/ff7_re_dataset.jsonl 2>&1
wc -l data/ff7_re_dataset.jsonl 2>&1

echo
echo "===== DONE ====="
