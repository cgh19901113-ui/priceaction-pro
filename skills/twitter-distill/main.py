"""
Twitter 数据收集 - 主控制器

一键完成：登录检查 → 自动收集 → 数据导出 → 回测分析
"""

import os
import sys
import subprocess
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

def run_command(cmd, description):
    """运行命令"""
    print(f"\n{'='*70}")
    print(f"[Step] {description}")
    print(f"{'='*70}")
    print(f"Running: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode == 0

def check_login():
    """检查是否已登录"""
    profile_dir = os.path.join(SCRIPT_DIR, "browser_profile")
    return os.path.exists(profile_dir) and os.path.isdir(profile_dir)

def main():
    print("\n" + "="*70)
    print("Twitter 数据收集 - 全自动化流程")
    print("="*70)
    
    # 步骤 1: 检查登录
    print("\n[1/4] 检查登录状态...")
    if not check_login():
        print("\n[!] 首次使用，需要先登录 Twitter")
        print("\n正在启动登录流程...")
        
        if not run_command(
            [sys.executable, "setup_login.py"],
            "Twitter 登录设置"
        ):
            print("\n[Error] 登录失败，请重试")
            return False
        
        print("\n[OK] 登录完成！请重新运行此脚本继续收集")
        print("\n命令：python main.py")
        return True
    
    print("[OK] 已登录")
    
    # 步骤 2: 自动收集
    print("\n[2/4] 开始自动收集...")
    if not run_command(
        [sys.executable, "run_auto.py"],
        "Twitter 数据收集（10 位博主，目标 1000 条/人）"
    ):
        print("\n[Error] 收集中断")
        return False
    
    # 步骤 3: 导出回测数据
    print("\n[3/4] 导出回测数据...")
    if not run_command(
        [sys.executable, "run_auto.py", "--export"],
        "数据导出"
    ):
        print("\n[Error] 导出失败")
        return False
    
    # 步骤 4: 运行回测
    print("\n[4/4] 运行回测分析...")
    backtest_script = os.path.join(SCRIPT_DIR, "..", "..", "strategy", "backtest_twitter.py")
    if not run_command(
        [sys.executable, backtest_script],
        "策略回测"
    ):
        print("\n[Error] 回测失败")
        return False
    
    # 完成
    print("\n" + "="*70)
    print("✅ 全部完成！")
    print("="*70)
    print("\n输出文件:")
    print(f"  - 原始数据：data/twitter/*.jsonl")
    print(f"  - 回测数据：strategy/twitter_recommendations.json")
    print(f"  - 回测结果：strategy/backtest_twitter_result.csv (如有)")
    print("\n查看进度：cat progress.json")
    print("="*70)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
