#!/bin/bash
# 启动Gradio应用脚本

source /opt/anaconda3/etc/profile.d/conda.sh
conda activate agent_env

cd /Users/chenkai/Downloads/AGENT_DEMO

echo "正在启动TCL智能产品咨询助手..."
python src/ui/gradio_app.py 2>&1 | tee logs/gradio.log