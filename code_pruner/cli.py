"""CLI 入口: code-pruner <文件> <剪枝条件>"""
import sys


def main():
    if len(sys.argv) < 3:
        print("用法: code-pruner <文件> <剪枝条件>")
        print("示例: code-pruner user.py '删除没用到的方法'")
        sys.exit(1)
    
    file, condition = sys.argv[1], sys.argv[2]
    print(f"目标文件: {file}")
    print(f"剪枝条件: {condition}")
    print("[TODO: 实现剪枝逻辑]")


if __name__ == "__main__":
    main()
