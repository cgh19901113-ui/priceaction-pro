"""
Twitter 登录设置 - 首次使用运行一次

打开浏览器，手动登录 Twitter
登录后 Cookie 会保存，之后可全自动运行
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright

def setup_login():
    """设置登录"""
    print("\n" + "="*70)
    print("Twitter 登录设置")
    print("="*70)
    print("\n说明:")
    print("1. 浏览器会打开，请手动登录 Twitter")
    print("2. 登录后关闭浏览器，Cookie 会自动保存")
    print("3. 之后运行 crawler_auto.py 即可全自动收集")
    print("="*70)
    
    user_data_dir = os.path.join(os.path.dirname(__file__), "browser_profile")
    os.makedirs(user_data_dir, exist_ok=True)
    
    print(f"\n[Info] Profile directory: {user_data_dir}")
    print("\n正在打开浏览器...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,  # 显示浏览器
            viewport={'width': 1280, 'height': 800},
        )
        
        page = browser.new_page()
        page.goto("https://x.com/login", timeout=60000)
        
        print("\n[Info] 浏览器已打开，请在 2 分钟内手动登录 Twitter...")
        print("[Info] 登录后 30 秒自动检测并关闭...")
        
        # 等待登录（最长 2 分钟）
        for i in range(24):  # 2 分钟，每 5 秒检查一次
            time.sleep(5)
            
            # 检查是否已登录
            try:
                page.goto("https://x.com/home", timeout=30000)
                time.sleep(2)
                
                if not page.query_selector('input[autocomplete="username"]'):
                    print("\n[OK] 检测到登录状态！")
                    break
                else:
                    print(f"[Wait] 等待登录... ({(i+1)*5}s/120s)")
            except:
                continue
        
        # 最终验证
        try:
            page.goto("https://x.com/home", timeout=30000)
            time.sleep(2)
            
            if page.query_selector('input[autocomplete="username"]'):
                print("\n[Error] 2 分钟内未检测到登录，请重新运行")
            else:
                print("\n[OK] 登录成功！Cookie 已保存")
                print("\n[Next] 现在可以运行全自动收集:")
                print("  python crawler_auto.py")
        except:
            print("\n[Error] 验证失败")
        
        browser.close()

if __name__ == "__main__":
    setup_login()
