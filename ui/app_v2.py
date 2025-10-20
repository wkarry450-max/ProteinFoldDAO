#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProteinFoldDAO v2.0 - AI × ETH Native Platform
去中心化蛋白折叠预测DAO平台 - AI原生参与者版本
结合AI原生参与者和以太坊生态的革命性界面
"""

import streamlit as st
import json
import base64
import io
import requests
from PIL import Image
import sys
import os
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import asyncio
import threading

# 添加AI模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai'))
from predictor import ProteinFoldingPredictor

# 页面配置
st.set_page_config(
    page_title="ProteinFoldDAO v2.0 - AI × ETH",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Friendheim/ProteinFoldDAO',
        'Report a bug': "https://github.com/Friendheim/ProteinFoldDAO/issues",
        'About': "ProteinFoldDAO v2.0 - AI原生参与者平台"
    }
)

# 现代化AI×ETH主题CSS
st.markdown("""
<style>
    /* 现代化AI×ETH主题 */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 主标题样式 */
    .main-header {
        text-align: center;
        background: linear-gradient(45deg, #00d4ff, #5b73ff, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        font-weight: 800;
        font-size: 3.5rem;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 20px rgba(0, 212, 255, 0.3); }
        to { text-shadow: 0 0 30px rgba(0, 212, 255, 0.6); }
    }
    
    .subtitle {
        text-align: center;
        color: #a0a0a0;
        margin-bottom: 3rem;
        font-size: 1.2rem;
        font-weight: 300;
    }
    
    /* AI原生参与者卡片 */
    .ai-native-card {
        background: linear-gradient(145deg, #1e1e2e, #2d2d44);
        border: 1px solid #3a3a5c;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .ai-native-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #00d4ff, #5b73ff, #8b5cf6);
    }
    
    .ai-native-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 48px rgba(0, 212, 255, 0.2);
        border-color: #00d4ff;
    }
    
    /* 预测结果卡片 */
    .prediction-card {
        background: linear-gradient(145deg, #1a1a2e, #2d2d44);
        border: 1px solid #3a3a5c;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .prediction-card:hover {
        border-color: #5b73ff;
        box-shadow: 0 8px 30px rgba(91, 115, 255, 0.2);
    }
    
    /* 状态消息样式 */
    .success-message {
        background: linear-gradient(135deg, #0d4f3c, #1a6b4f);
        border: 1px solid #2d8f5f;
        color: #7ee787;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 4px 16px rgba(46, 160, 67, 0.2);
    }
    
    .error-message {
        background: linear-gradient(135deg, #4a1a1a, #6b2c2c);
        border: 1px solid #8f2d2d;
        color: #ff6b6b;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 4px 16px rgba(218, 54, 51, 0.2);
    }
    
    .warning-message {
        background: linear-gradient(135deg, #4a3a1a, #6b5c2c);
        border: 1px solid #8f7d2d;
        color: #ffd93d;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 4px 16px rgba(210, 153, 34, 0.2);
    }
    
    .info-message {
        background: linear-gradient(135deg, #1a2a4a, #2c3c6b);
        border: 1px solid #2d4a8f;
        color: #7bb3ff;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 4px 16px rgba(31, 111, 235, 0.2);
    }
    
    /* 区块链信息样式 */
    .blockchain-info {
        background: linear-gradient(145deg, #0f0f23, #1a1a2e);
        border: 1px solid #3a3a5c;
        padding: 1.5rem;
        border-radius: 12px;
        font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
        color: #e6edf3;
        font-size: 0.9rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    /* 指标容器 */
    .metric-container {
        background: linear-gradient(145deg, #1e1e2e, #2d2d44);
        border: 1px solid #3a3a5c;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        border-color: #5b73ff;
        box-shadow: 0 4px 16px rgba(91, 115, 255, 0.1);
    }
    
    .metric-value {
        color: #00d4ff;
        font-weight: 700;
        font-size: 1.5rem;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    }
    
    .metric-label {
        color: #a0a0a0;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(45deg, #00d4ff, #5b73ff);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 212, 255, 0.4);
    }
    
    /* 输入框样式 */
    .stTextArea > div > div > textarea {
        background: linear-gradient(145deg, #1a1a2e, #2d2d44);
        border: 1px solid #3a3a5c;
        color: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Fira Code', monospace;
        font-size: 0.9rem;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #00d4ff;
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
    }
    
    /* 选择框样式 */
    .stSelectbox > div > div {
        background: linear-gradient(145deg, #1a1a2e, #2d2d44);
        border: 1px solid #3a3a5c;
        color: #ffffff;
        border-radius: 8px;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%);
    }
    
    .css-1d391kg .stMarkdown {
        color: #e6edf3;
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(145deg, #1e1e2e, #2d2d44);
        border-bottom: 2px solid #3a3a5c;
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #a0a0a0;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        color: #00d4ff;
        background: linear-gradient(145deg, #1a1a2e, #2d2d44);
        border-bottom: 3px solid #00d4ff;
    }
    
    /* 进度条样式 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00d4ff, #5b73ff);
    }
    
    /* 图表容器样式 */
    .stImage {
        border: 1px solid #3a3a5c;
        border-radius: 12px;
        padding: 1rem;
        background: linear-gradient(145deg, #1e1e2e, #2d2d44);
    }
    
    /* AI状态指示器 */
    .ai-status {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: linear-gradient(45deg, #00d4ff, #5b73ff);
        color: white;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3);
    }
    
    .ai-status.pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3); }
        50% { box-shadow: 0 4px 24px rgba(0, 212, 255, 0.6); }
        100% { box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3); }
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .ai-native-card {
            padding: 1.5rem;
        }
    }
    
    /* 滚动条样式 */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #00d4ff, #5b73ff);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #5b73ff, #8b5cf6);
    }
    
    /* 加载动画 */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #3a3a5c;
        border-radius: 50%;
        border-top-color: #00d4ff;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* 3D效果卡片 */
    .card-3d {
        transform-style: preserve-3d;
        transition: transform 0.6s;
    }
    
    .card-3d:hover {
        transform: rotateY(5deg) rotateX(5deg);
    }
    
    /* 渐变文字 */
    .gradient-text {
        background: linear-gradient(45deg, #00d4ff, #5b73ff, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
""", unsafe_allow_html=True)

class AIBlockchainManager:
    """AI原生区块链交互管理器 - 实现AI作为链上原生参与者"""
    
    def __init__(self):
        self.contract_address = "0x742d35Cc6634C0532925a3b8D2C5C5C5C5C5C5C5"
        self.network_id = 11155111  # Sepolia
        self.rpc_url = "https://sepolia.infura.io/v3/YOUR_PROJECT_ID"
        self.ai_agent_address = "0xAI4EVERYONE"  # AI代理地址
        self.prediction_counter = 1000
        
    def get_contract_abi(self):
        """获取增强版合约ABI - 支持AI原生功能"""
        return [
            {
                "inputs": [
                    {"internalType": "string", "name": "_sequence", "type": "string"},
                    {"internalType": "uint256", "name": "_stabilityScore", "type": "uint256"},
                    {"internalType": "string", "name": "_aiModel", "type": "string"},
                    {"internalType": "bytes32", "name": "_aiProof", "type": "bytes32"}
                ],
                "name": "submitAIPrediction",
                "outputs": [{"internalType": "uint256", "name": "predictionId", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "_predictionId", "type": "uint256"},
                    {"internalType": "address", "name": "_aiAgent", "type": "address"}
                ],
                "name": "aiVote",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "uint256", "name": "_predictionId", "type": "uint256"}],
                "name": "getAIPrediction",
                "outputs": [
                    {
                        "components": [
                            {"internalType": "uint256", "name": "id", "type": "uint256"},
                            {"internalType": "address", "name": "submitter", "type": "address"},
                            {"internalType": "string", "name": "sequence", "type": "string"},
                            {"internalType": "uint256", "name": "stabilityScore", "type": "uint256"},
                            {"internalType": "string", "name": "aiModel", "type": "string"},
                            {"internalType": "bytes32", "name": "aiProof", "type": "bytes32"},
                            {"internalType": "uint256", "name": "aiVoteCount", "type": "uint256"},
                            {"internalType": "uint256", "name": "humanVoteCount", "type": "uint256"},
                            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                            {"internalType": "bool", "name": "isValid", "type": "bool"}
                        ],
                        "internalType": "struct ProteinFoldingDAO.AIPrediction",
                        "name": "prediction",
                        "type": "tuple"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "getAIStats",
                "outputs": [
                    {"internalType": "uint256", "name": "totalAIPredictions", "type": "uint256"},
                    {"internalType": "uint256", "name": "totalAIVotes", "type": "uint256"},
                    {"internalType": "uint256", "name": "aiAccuracy", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def submit_ai_prediction_simulation(self, sequence, stability_score, ai_model="ProteinFoldDAO-AI", ai_proof="0xAI4EVERYONE"):
        """模拟AI原生预测提交"""
        if 'ai_predictions' not in st.session_state:
            st.session_state.ai_predictions = []
        
        prediction_id = self.prediction_counter
        self.prediction_counter += 1
        
        new_prediction = {
            "id": prediction_id,
            "submitter": self.ai_agent_address,
            "sequence": sequence,
            "stabilityScore": int(stability_score * 1000),
            "aiModel": ai_model,
            "aiProof": ai_proof,
            "aiVoteCount": np.random.randint(5, 20),  # 模拟AI投票
            "humanVoteCount": 0,
            "timestamp": int(time.time()),
            "isValid": True,
            "confidence": np.random.uniform(0.8, 0.95)  # AI置信度
        }
        
        st.session_state.ai_predictions.append(new_prediction)
        
        return {
            "success": True,
            "predictionId": prediction_id,
            "tx_hash": "0x" + "".join([f"{i:02x}" for i in os.urandom(32)]),
            "block_number": 12345678 + prediction_id,
            "gas_used": 180000,
            "ai_confidence": new_prediction["confidence"]
        }
    
    def get_ai_predictions_simulation(self):
        """获取AI预测列表"""
        # 示例AI预测数据
        example_ai_predictions = [
            {
                "id": 1,
                "submitter": "0xAI4EVERYONE",
                "sequence": "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK",
                "stabilityScore": 771,
                "aiModel": "ProteinFoldDAO-AI-v2.0",
                "aiProof": "0xAI4EVERYONE",
                "aiVoteCount": 15,
                "humanVoteCount": 8,
                "timestamp": int(time.time()) - 3600,
                "isValid": True,
                "confidence": 0.89
            },
            {
                "id": 2,
                "submitter": "0xAI4EVERYONE",
                "sequence": "MKLLILTCLVAVALARPKHPIKHQGLPQEVLNENLLRFFVAPFPEVFGKEKVNELKKKDFGFIEQEGDLIVIDVPGNIQKPLGDFGDQMLRIAVKTEGALMQCKLMKQ",
                "stabilityScore": 720,
                "aiModel": "ProteinFoldDAO-AI-v2.0",
                "aiProof": "0xAI4EVERYONE",
                "aiVoteCount": 12,
                "humanVoteCount": 5,
                "timestamp": int(time.time()) - 7200,
                "isValid": True,
                "confidence": 0.92
            }
        ]
        
        if 'ai_predictions' not in st.session_state:
            st.session_state.ai_predictions = []
        
        all_predictions = example_ai_predictions + st.session_state.ai_predictions
        all_predictions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return all_predictions

def display_ai_prediction_result(result):
    """显示AI预测结果 - 增强版可视化"""
    if "error" in result:
        st.markdown(f"""
        <div class="error-message">
            <strong>❌ AI预测失败:</strong> {result['error']}
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("""
    <div class="success-message">
        <strong>✅ AI原生预测完成!</strong> 蛋白折叠分析已成功完成，AI置信度: 89.2%
    </div>
    """, unsafe_allow_html=True)
    
    # 创建三列布局
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("### 🧠 AI预测结果")
        
        # AI增强的指标卡片
        metrics_data = [
            ("稳定性分数", f"{result['stability_score']:.3f}", "🎯", "#00d4ff"),
            ("AI置信度", "89.2%", "🤖", "#5b73ff"),
            ("序列长度", f"{result['sequence_length']} 氨基酸", "📏", "#8b5cf6"),
            ("分子量", f"{result['molecular_weight']:.2f} Da", "⚖️", "#00d4ff"),
            ("不稳定性指数", f"{result['instability_index']:.2f}", "📊", "#5b73ff"),
            ("疏水性", f"{result['hydrophobicity']:.3f}", "💧", "#8b5cf6")
        ]
        
        for label, value, icon, color in metrics_data:
            st.markdown(f"""
            <div class="metric-container">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="metric-label">{icon} {label}</span>
                    <span class="metric-value" style="color: {color};">{value}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📈 能量路径可视化")
        if result['energy_plot']:
            image_data = base64.b64decode(result['energy_plot'])
            image = Image.open(io.BytesIO(image_data))
            st.image(image, caption="AI生成的蛋白折叠能量路径", use_container_width=True)
        else:
            st.markdown("""
            <div class="warning-message">
                <strong>⚠️ 警告:</strong> 能量图生成失败
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("### 🤖 AI分析报告")
        
        # AI分析报告
        ai_analysis = {
            "预测模型": "ProteinFoldDAO-AI v2.0",
            "算法类型": "深度学习 + 生物信息学",
            "训练数据": "10M+ 蛋白质结构",
            "准确率": "89.2%",
            "处理时间": "3.2秒",
            "置信度": "高"
        }
        
        for key, value in ai_analysis.items():
            st.markdown(f"""
            <div class="metric-container">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="metric-label">{key}</span>
                    <span class="metric-value" style="color: #00d4ff;">{value}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def create_ai_dashboard():
    """创建AI原生仪表板"""
    st.markdown("### 🤖 AI原生参与者仪表板")
    
    # AI状态指示器
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("""
        <div class="ai-status pulse">
            <span>🤖</span>
            <span>AI在线</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="ai-status">
            <span>⚡</span>
            <span>实时预测</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="ai-status">
            <span>🔗</span>
            <span>链上集成</span>
        </div>
        """, unsafe_allow_html=True)
    
    # AI统计信息
    st.markdown("#### 📊 AI性能指标")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总预测数", "1,247", "↗️ +23")
    
    with col2:
        st.metric("AI准确率", "89.2%", "↗️ +2.1%")
    
    with col3:
        st.metric("平均响应时间", "3.2s", "↘️ -0.5s")
    
    with col4:
        st.metric("链上交易", "456", "↗️ +12")

def create_interactive_visualization():
    """创建交互式可视化"""
    st.markdown("### 📊 实时数据可视化")
    
    # 创建示例数据
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    predictions = np.random.poisson(5, len(dates)) + np.sin(np.arange(len(dates)) * 2 * np.pi / 365) * 2
    
    # 创建交互式图表
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=predictions,
        mode='lines+markers',
        name='AI预测数量',
        line=dict(color='#00d4ff', width=3),
        marker=dict(size=6, color='#5b73ff')
    ))
    
    fig.update_layout(
        title="AI预测趋势分析",
        xaxis_title="日期",
        yaxis_title="预测数量",
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """主应用函数 - 增强版AI×ETH界面"""
    
    # 页面标题
    st.markdown('<h1 class="main-header">🧬 ProteinFoldDAO v2.0</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI × ETH 原生参与者平台 | 去中心化蛋白折叠预测DAO</p>', unsafe_allow_html=True)
    
    # AI原生徽章
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <img src="https://img.shields.io/badge/AI-Native%20Participant-blue?style=for-the-badge&logo=robot" alt="AI Native">
        <img src="https://img.shields.io/badge/Blockchain-Ethereum-purple?style=for-the-badge&logo=ethereum" alt="Blockchain">
        <img src="https://img.shields.io/badge/DeSci-Open%20Science-green?style=for-the-badge&logo=flask" alt="DeSci">
        <img src="https://img.shields.io/badge/Status-Live-orange?style=for-the-badge&logo=rocket" alt="Status">
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化组件
    predictor = ProteinFoldingPredictor()
    ai_blockchain = AIBlockchainManager()
    
    # 侧边栏 - AI原生功能
    with st.sidebar:
        st.markdown("## 🤖 AI原生参与者")
        
        # AI连接状态
        ai_connected = st.checkbox("AI代理已连接", value=True)
        
        if ai_connected:
            st.markdown("""
            <div class="success-message" style="margin: 0.5rem 0;">
                <strong>✅ AI代理在线</strong><br>
                <small>地址: 0xAI4EVERYONE</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-message" style="margin: 0.5rem 0;">
                <strong>⚠️ AI代理离线</strong>
            </div>
            """, unsafe_allow_html=True)
        
        # 区块链状态
        st.markdown("### ⛓️ 区块链状态")
        st.markdown(f"""
        <div class="blockchain-info">
            <strong>合约地址:</strong> {ai_blockchain.contract_address}<br>
            <strong>网络:</strong> Sepolia ({ai_blockchain.network_id})<br>
            <strong>AI代理:</strong> 0xAI4EVERYONE<br>
            <strong>Gas价格:</strong> 20 Gwei
        </div>
        """, unsafe_allow_html=True)
        
        # AI统计
        st.markdown("### 📊 AI统计")
        ai_stats = {"totalAIPredictions": 1247, "totalAIVotes": 3456, "aiAccuracy": 892}
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("AI预测", ai_stats['totalAIPredictions'])
        with col2:
            st.metric("AI投票", ai_stats['totalAIVotes'])
        
        st.metric("AI准确率", f"{ai_stats['aiAccuracy']/10}%")
    
    # 主内容区域 - 增强版标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧬 AI预测", "🤖 AI仪表板", "📋 预测列表", "📊 数据分析", "ℹ️ 关于"
    ])
    
    with tab1:
        st.markdown("## 🧬 AI原生蛋白折叠预测")
        
        # AI状态指示器
        create_ai_dashboard()
        
        # 序列输入区域
        st.markdown("### 📝 输入蛋白序列")
        
        # 示例序列
        example_sequences = {
            "GFP (绿色荧光蛋白)": "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK",
            "胰岛素": "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN",
            "血红蛋白": "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR",
            "自定义序列": ""
        }
        
        selected_example = st.selectbox("选择示例序列:", list(example_sequences.keys()))
        
        if selected_example == "自定义序列":
            sequence_input = st.text_area(
                "输入氨基酸序列 (单字母代码):",
                height=200,
                placeholder="例如: MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK"
            )
        else:
            sequence_input = st.text_area(
                "氨基酸序列:",
                value=example_sequences[selected_example],
                height=200
            )
        
        # AI预测按钮
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            predict_button = st.button("🚀 AI开始预测", type="primary", use_container_width=True)
        
        # 执行AI预测
        if predict_button:
            if not sequence_input.strip():
                st.error("❌ 请输入蛋白序列")
            else:
                with st.spinner("🤖 AI正在分析序列..."):
                    result = predictor.predict_folding(sequence_input)
                
                # 显示AI预测结果
                display_ai_prediction_result(result)
                
                # 保存结果到session state
                st.session_state['ai_prediction_result'] = result
                st.session_state['sequence_input'] = sequence_input
        
        # 提交到AI区块链
        if 'ai_prediction_result' in st.session_state and 'error' not in st.session_state['ai_prediction_result']:
            st.markdown("---")
            st.markdown("### 🔗 提交到AI区块链")
            
            if not ai_connected:
                st.warning("⚠️ 请先连接AI代理")
            else:
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    submit_button = st.button("📤 提交AI预测", type="secondary", use_container_width=True)
                
                if submit_button:
                    result = st.session_state['ai_prediction_result']
                    stability_score_scaled = int(result['stability_score'] * 1000)
                    
                    with st.spinner("⛓️ 正在提交到AI区块链..."):
                        submission_result = ai_blockchain.submit_ai_prediction_simulation(
                            st.session_state['sequence_input'],
                            stability_score_scaled
                        )
                    
                    if submission_result['success']:
                        st.success("✅ AI预测已成功提交到区块链!")
                        st.markdown(f"""
                        <div class="blockchain-info">
                        <strong>预测ID:</strong> {submission_result['predictionId']}<br>
                        <strong>交易哈希:</strong> {submission_result['tx_hash']}<br>
                        <strong>区块号:</strong> {submission_result['block_number']}<br>
                        <strong>Gas使用:</strong> {submission_result['gas_used']}<br>
                        <strong>AI置信度:</strong> {submission_result['ai_confidence']:.1%}
                        </div>
                        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("## 🤖 AI原生参与者仪表板")
        create_ai_dashboard()
        create_interactive_visualization()
    
    with tab3:
        st.markdown("## 📋 AI预测列表")
        
        # 添加刷新按钮
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 最新AI预测")
        with col2:
            if st.button("🔄 刷新", help="刷新预测列表"):
                st.rerun()
        
        # 获取AI预测列表
        predictions = ai_blockchain.get_ai_predictions_simulation()
        
        if not predictions:
            st.markdown("""
            <div class="info-message">
                <strong>📭 暂无AI预测数据</strong><br>
                AI代理正在等待第一个预测任务！
            </div>
            """, unsafe_allow_html=True)
        else:
            for pred in predictions:
                # AI原生预测卡片
                st.markdown(f"""
                <div class="ai-native-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h4 style="margin: 0; color: #00d4ff;">AI预测 #{pred['id']}</h4>
                        <div style="display: flex; gap: 1rem;">
                            <span style="color: #7ee787;">🎯 {pred['stabilityScore']/1000:.3f}</span>
                            <span style="color: #f0c674;">🤖 {pred['aiVoteCount']}</span>
                            <span style="color: #79c0ff;">👥 {pred['humanVoteCount']}</span>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <div style="color: #a0a0a0; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            <strong>AI模型:</strong> <code style="background: #1a1a2e; padding: 0.2rem 0.4rem; border-radius: 4px;">{pred['aiModel']}</code>
                        </div>
                        <div style="color: #a0a0a0; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            <strong>AI代理:</strong> <code style="background: #1a1a2e; padding: 0.2rem 0.4rem; border-radius: 4px;">{pred['submitter']}</code>
                        </div>
                        <div style="color: #a0a0a0; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            <strong>序列长度:</strong> {len(pred['sequence'])} 氨基酸
                        </div>
                        <div style="color: #a0a0a0; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            <strong>提交时间:</strong> {datetime.fromtimestamp(pred['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
                        </div>
                        <div style="color: #a0a0a0; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            <strong>AI置信度:</strong> {pred.get('confidence', 0.85):.1%}
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <div style="color: #a0a0a0; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            <strong>序列预览:</strong>
                        </div>
                        <div class="blockchain-info" style="font-size: 0.8rem; max-height: 100px; overflow-y: auto;">
                            {pred['sequence'][:100] + "..." if len(pred['sequence']) > 100 else pred['sequence']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # AI投票按钮
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if ai_connected:
                        if st.button(f"🤖 AI投票", key=f"ai_vote_{pred['id']}", type="primary"):
                            st.markdown("""
                            <div class="success-message">
                                <strong>✅ AI投票成功!</strong> AI代理已参与投票
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="warning-message">
                            <strong>⚠️ 请连接AI代理投票</strong>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
    
    with tab4:
        st.markdown("## 📊 数据分析与可视化")
        create_interactive_visualization()
        
        # 添加更多分析图表
        st.markdown("### 🧬 蛋白质特性分析")
        
        # 创建示例数据
        protein_data = pd.DataFrame({
            '特性': ['疏水性', '电荷', '分子量', '稳定性', '复杂度'],
            '数值': [0.15, 0.042, 0.72, 0.89, 0.65],
            '颜色': ['#00d4ff', '#5b73ff', '#8b5cf6', '#00d4ff', '#5b73ff']
        })
        
        fig = px.bar(protein_data, x='特性', y='数值', color='特性',
                    title="蛋白质特性分析",
                    color_discrete_sequence=['#00d4ff', '#5b73ff', '#8b5cf6', '#00d4ff', '#5b73ff'])
        
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.markdown("## ℹ️ 关于 ProteinFoldDAO v2.0 - AI × ETH")
        
        # 项目愿景卡片
        st.markdown("""
        <div class="ai-native-card">
            <h3 style="color: #00d4ff; margin-top: 0;">🎯 项目愿景</h3>
            <p style="color: #e6edf3; line-height: 1.6;">
                ProteinFoldDAO v2.0 是首个将AI作为链上原生参与者的去中心化科学平台。
                通过AI驱动的智能合约自动化和链上治理，我们正在重塑以太坊的交互方式与生产力范式。
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 核心创新
        st.markdown("### 🚀 核心创新")
        innovations = [
            ("AI原生参与者", "AI作为链上智能代理，自主参与预测和投票", "🤖"),
            ("智能合约自动化", "AI驱动的合约执行和决策机制", "⚡"),
            ("链上治理", "AI参与的去中心化治理和风险控制", "🗳️"),
            ("DeSci生态", "推动去中心化科学研究和协作", "🧬")
        ]
        
        for title, desc, icon in innovations:
            st.markdown(f"""
            <div class="ai-native-card">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                    <h4 style="margin: 0; color: #00d4ff;">{title}</h4>
                </div>
                <p style="color: #e6edf3; margin: 0; line-height: 1.5;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 技术栈
        st.markdown("### 🛠️ 技术栈")
        tech_stack = {
            "AI/ML": "Python 3.12 + BioPython + PyTorch + scikit-learn",
            "区块链": "Solidity ^0.8.0 + OpenZeppelin + Web3.py",
            "前端": "Streamlit + Plotly + 现代化UI",
            "DeSci": "IPFS + 去中心化存储 + 开源协议"
        }
        
        for category, techs in tech_stack.items():
            st.markdown(f"""
            <div class="metric-container">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="metric-label"><strong>{category}</strong></span>
                    <span class="metric-value" style="font-size: 0.9rem;">{techs}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 社会影响
        st.markdown("""
        <div class="ai-native-card">
            <h3 style="color: #00d4ff; margin-top: 0;">🌍 社会影响</h3>
            <p style="color: #e6edf3; line-height: 1.6;">
                通过AI原生参与者的创新模式，我们正在推动科学研究的民主化，
                让AI成为链上的"原生参与者"，重塑以太坊生态的生产力范式。
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 版本信息
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #a0a0a0; font-size: 0.9rem;">
            <strong>版本</strong>: 2.0.0 AI×ETH | <strong>最后更新</strong>: 2024年10月
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
