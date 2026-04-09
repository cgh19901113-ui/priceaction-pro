# PriceAction-SaaS 本地测试脚本

**用途**: 本地运行测试 API，验证后端是否正常

## 运行方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行本地服务
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. 测试 API
curl http://localhost:8000/api/health
curl "http://localhost:8000/api/analyze?symbol=600519"
```

## 预期输出

### 健康检查
```json
{"status": "healthy"}
```

### 股票分析
```json
{
  "success": true,
  "symbol": "600519",
  "analysis": {
    "大周期": "看涨",
    "大周期_颜色": "🟢",
    "趋势持续": "2 天",
    ...
  }
}
```

## 故障排查

### 问题 1: 模块未找到
```
ModuleNotFoundError: No module named 'fastapi'
```
**解决**: `pip install -r requirements.txt`

### 问题 2: 数据获取失败
```
Error fetching 600519: ...
```
**解决**: 检查网络连接，Akshare 需要访问外网

### 问题 3: 端口被占用
```
Error: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```
**解决**: 换端口 `--port 8001`
