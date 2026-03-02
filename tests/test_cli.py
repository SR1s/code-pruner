"""CLI 测试"""
import subprocess
import sys


def test_cli_help():
    """测试 CLI 帮助信息"""
    result = subprocess.run(
        [sys.executable, "-m", "code_pruner.cli"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 1
    assert "用法:" in result.stdout or "用法:" in result.stderr


def test_cli_with_args():
    """测试带参数的 CLI"""
    result = subprocess.run(
        [sys.executable, "-m", "code_pruner.cli", "user.py", "删除没用到的方法"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "目标文件: user.py" in result.stdout
    assert "剪枝条件: 删除没用到的方法" in result.stdout
