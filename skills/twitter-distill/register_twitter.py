"""
Twitter 账号注册 + 数据收集自动化

流程：
1. 使用临时邮箱注册 Twitter
2. 保存登录凭证
3. 自动收集博主数据
"""

import os
import sys
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 临时邮箱服务（10 分钟邮箱）
TEMP_MAIL_URL = "https://www.10minutemail.com"

# 账号信息
ACCOUNT_INFO = {
    "username": f"DataCollector{datetime.now().strftime('%Y%m%d')}",
    "email": None,  # 从临时邮箱获取
    "password": f"AutoPass{datetime.now().strftime('%Y%m%d')}!@#",
}

def get_temp_email():
    """获取临时邮箱地址"""
    print("[Email] Getting temporary email...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(TEMP_MAIL_URL, timeout=30000)
            time.sleep(5)
            
            # 提取邮箱地址
            email_el = page.query_selector('#copyField')
            if email_el:
                email = email_el.get_attribute('value')
                print(f"[OK] Temporary email: {email}")
                return email
            else:
                # 尝试其他选择器
                email_el = page.query_selector('input[readonly]')
                if email_el:
                    email = email_el.get_attribute('value')
                    print(f"[OK] Temporary email: {email}")
                    return email
            
            print("[Error] Could not get email address")
            return None
        
        except Exception as e:
            print(f"[Error] {e}")
            return None
        
        finally:
            browser.close()

def register_twitter(username: str, email: str, password: str):
    """
    注册 Twitter 账号
    
    注意：Twitter 注册需要手机号验证，这可能无法自动化完成
    如果注册失败，我们会使用备用方案
    """
    print(f"\n[Register] Attempting to register @{username}")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    
    with sync_playwright() as p:
        user_data_dir = os.path.join(os.path.dirname(__file__), "browser_profile")
        os.makedirs(user_data_dir, exist_ok=True)
        
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,  # 显示浏览器，方便手动处理验证
            viewport={'width': 1280, 'height': 800},
        )
        
        page = browser.new_page()
        
        try:
            # 访问注册页面
            page.goto("https://x.com/i/flow/signup", timeout=60000)
            time.sleep(5)
            
            print("\n[Info] 注册页面已打开")
            print("[Info] 请手动完成注册流程（包括手机验证）")
            print("[Info] 注册完成后按 Enter 继续...")
            
            # 等待用户完成注册
            input()
            
            # 验证登录状态
            page.goto("https://x.com/home", timeout=60000)
            time.sleep(3)
            
            if page.query_selector('input[autocomplete="username"]'):
                print("\n[Error] 注册/登录失败")
                return False
            else:
                print("\n[OK] 注册成功！账号信息已保存")
                
                # 保存账号信息
                ACCOUNT_INFO['email'] = email
                save_account_info()
                return True
        
        except Exception as e:
            print(f"[Error] {e}")
            return False
        
        finally:
            browser.close()

def save_account_info():
    """保存账号信息"""
    info_file = os.path.join(os.path.dirname(__file__), "twitter_account.json")
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(ACCOUNT_INFO, f, indent=2, ensure_ascii=False)
    print(f"[Save] Account info saved to {info_file}")

def load_account_info():
    """加载账号信息"""
    info_file = os.path.join(os.path.dirname(__file__), "twitter_account.json")
    if os.path.exists(info_file):
        with open(info_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def main():
    print("\n" + "="*70)
    print("Twitter 账号注册助手")
    print("="*70)
    
    # 检查是否已有账号
    existing = load_account_info()
    if existing:
        print("\n[Info] 已有保存的账号:")
        print(f"  Username: {existing.get('username')}")
        print(f"  Email: {existing.get('email')}")
        print("\n[Q] 使用已有账号还是注册新的？")
        print("  1. 使用已有账号 (运行 python run_auto.py)")
        print("  2. 注册新账号")
        choice = input("\n选择 (1/2): ").strip()
        
        if choice == "1":
            print("\n[OK] 请运行：python run_auto.py")
            return
        # 否则继续注册
    
    # 获取临时邮箱
    email = get_temp_email()
    if not email:
        print("\n[Error] 无法获取临时邮箱")
        print("\n备用方案:")
        print("  1. 使用你自己的邮箱注册")
        print("  2. 访问 https://www.10minutemail.com 手动获取邮箱")
        email = input("\n请输入邮箱地址：").strip()
    
    # 注册 Twitter
    print("\n" + "-"*70)
    print("注意：Twitter 注册需要手机号验证")
    print("如果自动注册失败，请手动完成验证")
    print("-"*70)
    
    success = register_twitter(
        ACCOUNT_INFO['username'],
        email,
        ACCOUNT_INFO['password']
    )
    
    if success:
        print("\n" + "="*70)
        print("✅ 注册完成！")
        print("="*70)
        print("\n下一步:")
        print("  python run_auto.py  # 开始自动收集数据")
    else:
        print("\n" + "="*70)
        print("⚠️ 注册未完成")
        print("="*70)
        print("\n建议:")
        print("  1. 手动访问 https://x.com 注册账号")
        print("  2. 使用已有 Twitter 账号")
        print("  3. 使用其他方式获取数据（如 API）")

if __name__ == "__main__":
    main()
