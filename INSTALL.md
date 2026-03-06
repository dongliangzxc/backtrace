# 安装指南

## 依赖包说明

本项目依赖以下核心包：

- **akshare**: 金融数据获取库
- **akquant**: 高性能回测引擎
- **pandas**: 数据处理
- **numpy**: 数值计算
- **pyarrow**: Parquet文件支持

## 安装步骤

### 方式1：使用 requirements.txt（推荐）

```bash
pip install -r requirements.txt
```

### 方式2：手动安装

```bash
# 安装核心包
pip install akshare>=1.14.0
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install pyarrow>=14.0.0

# 安装akquant（注意版本兼容性）
pip install akquant
```

## 版本兼容性说明

### akquant 版本选择

akquant的不同版本对pandas有不同要求：

- **akquant 0.1.31+**: 要求 pandas >= 3.0.0
- **akquant 0.1.22-0.1.30**: 要求 pandas >= 2.0.0
- **akquant < 0.1.22**: 要求 pandas >= 1.5.0

**建议配置（稳定版本）:**

```bash
pip install akquant==0.1.22 pandas==2.2.3 akshare>=1.14.0
```

### 常见问题

#### Q1: akquant 安装失败

**症状**: 提示编译错误或找不到预编译版本

**解决方案**:
1. 确保使用预编译的wheel版本，避开需要编译的版本
2. 检查Python版本（推荐Python 3.10+）
3. 尝试指定特定版本：
   ```bash
   pip install akquant==0.1.22
   ```

#### Q2: pandas版本冲突

**症状**: 提示 "Could not find a version that satisfies the requirement pandas>=3.0.0"

**解决方案**:
1. 降低akquant版本到0.1.22-0.1.30区间
2. 或升级pandas到3.0+（注意其他包的兼容性）

#### Q3: 在Apple Silicon (M1/M2) Mac上安装

**特殊说明**: 
- 确保使用arm64架构的wheel包
- akquant从0.1.16+开始支持macOS arm64

```bash
# 查看当前Python架构
python -c "import platform; print(platform.machine())"

# 应该输出 arm64
```

## 验证安装

运行以下命令验证安装是否成功：

```python
# 测试脚本
import akshare as ak
import akquant as aq
import pandas as pd
import numpy as np

print(f"akshare版本: {ak.__version__}")
print(f"akquant版本: {aq.__version__}")
print(f"pandas版本: {pd.__version__}")
print(f"numpy版本: {np.__version__}")
print("\n✅ 所有依赖包安装成功！")
```

保存为 `test_install.py` 并运行：

```bash
python test_install.py
```

## 推荐环境

- **操作系统**: macOS / Linux / Windows
- **Python版本**: 3.10+
- **内存**: 建议 4GB+
- **磁盘空间**: 建议预留 2GB+ 用于数据缓存

## 推荐方式：conda 环境

由于 `akquant` 依赖 Rust 工具链编译，**强烈建议使用 conda 管理环境**，避免与系统 Python 或 IDE 内置虚拟环境冲突。

```bash
# 创建并激活 conda 环境
conda create -n backtest python=3.11 -y
conda activate backtest

# 安装依赖
pip install -r requirements.txt

# 将项目注册到该环境（只需执行一次）
pip install -e .
```

安装完成后，编辑 `run.sh` 将 Python 路径改为你的 conda 环境路径：

```bash
# run.sh 中修改这一行
PYTHON="/path/to/miniconda3/envs/backtest/bin/python"
```

之后所有脚本统一通过 `bash run.sh` 启动：

```bash
bash run.sh examples/eger_scan.py
bash run.sh examples/eger_backtest.py
```

## ⚠️ 已知问题：IDE 自动激活 .venv

部分 IDE（如 VS Code / Comate）会在项目根目录存在 `.venv` 时，自动在终端中执行 `source .venv/bin/activate`，导致 conda 环境被覆盖、`backtest` 模块找不到。

**解决方案**：直接使用 `bash run.sh <脚本>` 运行，脚本内部已硬编码正确的 Python 路径，不受 IDE 终端环境影响。

## 获取帮助

如果遇到安装问题，请：

1. 检查 Python 版本和架构（`python --version` 及 `which python`）
2. 确认是否在正确的 conda 环境中（`conda env list`）
3. 查看详细错误信息
4. 在项目 Issue 中报告问题（附上错误日志和环境信息）