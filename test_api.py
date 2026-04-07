import requests
import sys

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

# 测试 API
print("测试 PriceAction Pro API")
print("=" * 50)

# 1. 健康检查
r = requests.get("http://localhost:8000/api/health")
print(f"健康检查：{r.json()}")

# 2. 热门股票
r = requests.get("http://localhost:8000/api/popular")
stocks = r.json()['stocks']
print(f"\n热门股票：{', '.join([s['symbol'] for s in stocks])}")

# 3. 分析股票
print("\n分析贵州茅台 (600519.ss)...")
r = requests.post("http://localhost:8000/api/analyze", json={"symbol": "600519.ss"})

if r.status_code == 200:
    data = r.json()
    print(f"分析成功！剩余积分：{data['remaining_credits']}")
    
    analysis = data['analysis']
    print(f"\\n股票代码：{analysis['symbol']}")
    print(f"评分：{analysis['score']}分")
    print(f"建议：{analysis['recommendation']}")
    print(f"简评：{analysis['comment']}")
    
    print("\\n指标详情:")
    indicators = analysis['indicators']
    for key in ['大周期', '趋势持续', '大盘对比', '主力量能', '10 日振幅', '当前信号']:
        color = indicators.get(f'{key}_颜色', '')
        value = indicators.get(key, '')
        print(f"  {key}: {value} {color}")
else:
    print(f"分析失败：{r.status_code} - {r.text}")

print("\\n" + "=" * 50)
print("测试完成")
