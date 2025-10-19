# ProteinFoldDAO 部署指南

## 🚀 快速部署

### 1. 环境准备

#### 系统要求
- Python 3.12+
- Node.js 16+
- Git
- MetaMask钱包

#### 安装依赖
```bash
# 克隆项目
git clone https://github.com/your-username/ProteinFoldDAO.git
cd ProteinFoldDAO

# 安装AI模块依赖
pip install -r ai/requirements.txt

# 安装前端依赖
pip install -r ui/requirements.txt

# 安装区块链开发工具
cd contracts
npm install -g hardhat
npm install
```

### 2. AI模块测试

```bash
cd ai
python predictor.py
```

预期输出：
```
🧬 ProteinFoldDAO AI预测器测试
==================================================
✅ 序列长度: 238 氨基酸
✅ 稳定性分数: 0.720
✅ 分子量: 26180.00 Da
✅ 不稳定性指数: 45.20
✅ 疏水性: 0.150
✅ 电荷平衡: 0.042
✅ 能量图已生成: 12345 字符
📁 结果已保存到 prediction_result.json
```

### 3. 智能合约部署

#### 配置环境变量
```bash
# 创建 .env 文件
cd contracts
echo "PRIVATE_KEY=your_private_key_here" > .env
echo "INFURA_PROJECT_ID=your_infura_project_id" > .env
echo "ETHERSCAN_API_KEY=your_etherscan_api_key" > .env
```

#### 部署到Sepolia测试网
```bash
# 编译合约
npx hardhat compile

# 部署合约
npx hardhat run deploy.js --network sepolia
```

预期输出：
```
🚀 开始部署 ProteinFoldDAO 智能合约...
📝 部署账户: 0x742d35Cc6634C0532925a3b8D2C5C5C5C5C5C5C5
💰 账户余额: 0.5 ETH
📦 正在部署合约...
✅ 合约部署成功!
📍 合约地址: 0x1234567890123456789012345678901234567890
🔗 交易哈希: 0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
```

#### 验证合约
```bash
npx hardhat verify --network sepolia 0x1234567890123456789012345678901234567890
```

### 4. 前端应用启动

#### 配置合约地址
```bash
cd ui
# 编辑 app.py，更新合约地址
# CONTRACT_ADDRESS = "0x1234567890123456789012345678901234567890"
```

#### 启动Streamlit应用
```bash
streamlit run app.py
```

应用将在 `http://localhost:8501` 启动

### 5. 端到端测试

#### 运行集成测试
```bash
cd tests
python run_tests.py
```

#### 手动测试流程
1. 打开浏览器访问 `http://localhost:8501`
2. 在侧边栏勾选"MetaMask已连接"
3. 在"AI预测"标签页输入蛋白序列
4. 点击"开始预测"
5. 查看预测结果和能量图
6. 点击"提交预测"提交到区块链
7. 在"预测列表"标签页查看社区预测

## 🔧 高级配置

### 自定义AI模型

#### 修改预测算法
编辑 `ai/predictor.py` 中的 `calculate_stability_score` 方法：

```python
def calculate_stability_score(self, sequence: str) -> float:
    # 添加自定义算法
    custom_score = your_custom_algorithm(sequence)
    return custom_score
```

#### 集成预训练模型
```python
import torch
from transformers import AutoModel, AutoTokenizer

class AdvancedPredictor(ProteinFoldingPredictor):
    def __init__(self):
        super().__init__()
        self.model = AutoModel.from_pretrained("your-model")
        self.tokenizer = AutoTokenizer.from_pretrained("your-model")
    
    def predict_with_model(self, sequence):
        # 使用预训练模型预测
        pass
```

### 区块链网络配置

#### 添加新网络
编辑 `contracts/hardhat.config.js`：

```javascript
networks: {
  sepolia: {
    url: "https://sepolia.infura.io/v3/YOUR_PROJECT_ID",
    accounts: ["YOUR_PRIVATE_KEY"],
    chainId: 11155111
  },
  base: {
    url: "https://mainnet.base.org",
    accounts: ["YOUR_PRIVATE_KEY"],
    chainId: 8453
  }
}
```

#### 部署到Base网络
```bash
npx hardhat run deploy.js --network base
```

### 前端自定义

#### 添加新功能
编辑 `ui/app.py`：

```python
# 添加新的标签页
with st.tabs(["🧬 AI预测", "📋 预测列表", "🎨 可视化", "ℹ️ 关于"]):
    # 新功能实现
    pass
```

#### 集成IPFS存储
```python
import ipfshttpclient

def upload_to_ipfs(data):
    client = ipfshttpclient.connect()
    result = client.add_json(data)
    return result['Hash']
```

## 🐛 故障排除

### 常见问题

#### 1. AI预测失败
```bash
# 检查依赖
pip list | grep biopython
pip list | grep matplotlib

# 重新安装
pip install --upgrade biopython matplotlib
```

#### 2. 合约部署失败
```bash
# 检查网络连接
ping sepolia.infura.io

# 检查账户余额
npx hardhat run scripts/check-balance.js --network sepolia
```

#### 3. 前端启动失败
```bash
# 检查端口占用
netstat -an | grep 8501

# 使用其他端口
streamlit run app.py --server.port 8502
```

### 性能优化

#### AI预测优化
```python
# 使用缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_prediction(sequence):
    return predictor.predict_folding(sequence)
```

#### 前端优化
```python
# 使用会话状态
if 'predictions' not in st.session_state:
    st.session_state.predictions = []

# 避免重复计算
if 'last_sequence' not in st.session_state or st.session_state.last_sequence != sequence:
    result = predictor.predict_folding(sequence)
    st.session_state.last_sequence = sequence
    st.session_state.last_result = result
```

## 📊 监控和维护

### 日志记录
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('proteinfolddao.log'),
        logging.StreamHandler()
    ]
)
```

### 性能监控
```python
import time
import psutil

def monitor_performance():
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    print(f"CPU: {cpu_percent}%, Memory: {memory_percent}%")
```

### 数据备份
```bash
# 备份预测数据
cp prediction_result.json backup_$(date +%Y%m%d).json

# 备份合约状态
npx hardhat run scripts/backup-contract.js --network sepolia
```

## 🚀 生产部署

### Docker部署
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 云服务部署
```bash
# 部署到Heroku
heroku create proteinfolddao
git push heroku main

# 部署到AWS
aws ec2 run-instances --image-id ami-0c55b159cbfafe1d0 --instance-type t2.micro
```

## 📞 支持

- GitHub Issues: [项目问题](https://github.com/your-username/ProteinFoldDAO/issues)
- Discord: [社区讨论](https://discord.gg/your-invite)
- Email: support@proteinfolddao.com

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

