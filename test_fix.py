import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 测试 API
print("测试大盘对比修复")
print("=" * 50)

# 测试分析
print("\n分析 601888.ss (中国中免)...")
r = requests.post("http://localhost:8000/api/analyze", json={"symbol": "601888.ss"})

if r.status_code == 200:
    data = r.json()
    analysis = data['analysis']
    indicators = analysis['indicators']
    
    print(f"Symbol: {analysis['symbol']}")
    print(f"Score: {analysis['score']} pts")
    rec_text = analysis['recommendation'].replace('✅', '').replace('❌', '').replace('⚠️', '').replace('⚪', '')
    print(f"Rec: {rec_text}")
    
    print("\nIndicators:")
    for key in ['大周期', '趋势持续', '大盘对比', '主力量能', '10 日振幅', '当前信号']:
        color = indicators.get(f'{key}_颜色', '')
        value = indicators.get(key, '')
        print(f"  {key}: {value} {color}")
else:
    print(f"Failed: {r.status_code} - {r.text}")

print("\n" + "=" * 50)
