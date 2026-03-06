#!/bin/bash
# 股票回测工具启动脚本
# 用法：bash run.sh examples/eger_backtest.py
#       bash run.sh examples/simple_backtest.py
PYTHON="/Users/dongliang04/miniconda3/envs/markitdown/bin/python"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR"
exec "$PYTHON" "$@"