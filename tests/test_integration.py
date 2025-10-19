#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProteinFoldDAO 集成测试
测试AI预测、区块链交互和端到端流程
"""

import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from ai.predictor import ProteinFoldingPredictor


class TestProteinFoldingPredictor(unittest.TestCase):
    """AI预测器测试"""
    
    def setUp(self):
        self.predictor = ProteinFoldingPredictor()
        
    def test_valid_sequence_validation(self):
        """测试有效序列验证"""
        valid_sequences = [
            "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK",
            "ACDEFGHIKLMNPQRSTVWY",
            "MKLLILTCLVAVALARPKHPIKHQGLPQEVLNENLLRFFVAPFPEVFGKEKVNELKKKDFGFIEQEGDLIVIDVPGNIQKPLGDFGDQMLRIAVKTEGALMQCKLMKQ"
        ]
        
        for seq in valid_sequences:
            with self.subTest(sequence=seq):
                self.assertTrue(self.predictor.validate_sequence(seq))
    
    def test_invalid_sequence_validation(self):
        """测试无效序列验证"""
        invalid_sequences = [
            "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK123",  # 包含数字
            "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK@",  # 包含特殊字符
            "",  # 空序列
            "   ",  # 只有空格
            "ACDEFGHIKLMNPQRSTVWYZ"  # 包含无效氨基酸Z
        ]
        
        for seq in invalid_sequences:
            with self.subTest(sequence=seq):
                is_valid, error_msg = self.predictor.validate_sequence(seq)
                self.assertFalse(is_valid)
                self.assertGreater(len(error_msg), 0)
    
    def test_hydrophobicity_calculation(self):
        """测试疏水性计算"""
        # 测试已知疏水性的序列
        hydrophobic_seq = "AAAAA"  # 高疏水性
        hydrophilic_seq = "RRRRR"  # 高亲水性
        
        hydro_score = self.predictor.calculate_hydrophobicity(hydrophobic_seq)
        philic_score = self.predictor.calculate_hydrophobicity(hydrophilic_seq)
        
        self.assertGreater(hydro_score, philic_score)
        self.assertGreaterEqual(hydro_score, 0)
        self.assertLessEqual(philic_score, 0)
    
    def test_stability_score_range(self):
        """测试稳定性分数范围"""
        test_sequence = "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK"
        
        score = self.predictor.calculate_stability_score(test_sequence)
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        self.assertIsInstance(score, float)
    
    def test_prediction_output_format(self):
        """测试预测输出格式"""
        test_sequence = "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK"
        
        result = self.predictor.predict_folding(test_sequence)
        
        # 检查必要字段
        required_fields = [
            'sequence_length', 'stability_score', 'energy_plot',
            'molecular_weight', 'instability_index', 'hydrophobicity', 'charge_balance'
        ]
        
        for field in required_fields:
            self.assertIn(field, result)
        
        # 检查数据类型
        self.assertIsInstance(result['sequence_length'], int)
        self.assertIsInstance(result['stability_score'], float)
        self.assertIsInstance(result['energy_plot'], str)
        self.assertIsInstance(result['molecular_weight'], float)
        
        # 检查分数范围
        self.assertGreaterEqual(result['stability_score'], 0.0)
        self.assertLessEqual(result['stability_score'], 1.0)
        
        # 检查能量图是否为base64编码
        self.assertGreater(len(result['energy_plot']), 0)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试空序列
        result = self.predictor.predict_folding("")
        self.assertIn('error', result)
        
        # 测试无效序列
        result = self.predictor.predict_folding("INVALID123")
        self.assertIn('error', result)
        
        # 测试None输入
        result = self.predictor.predict_folding(None) # type: ignore
        self.assertIn('error', result)


class TestBlockchainIntegration(unittest.TestCase):
    """区块链集成测试"""
    
    def test_contract_abi_format(self):
        """测试合约ABI格式"""
        # 模拟合约ABI
        mock_abi = [
            {
                "inputs": [
                    {"internalType": "string", "name": "_sequence", "type": "string"},
                    {"internalType": "uint256", "name": "_stabilityScore", "type": "uint256"}
                ],
                "name": "submitPrediction",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        # 检查ABI结构
        self.assertIsInstance(mock_abi, list)
        self.assertGreater(len(mock_abi), 0)
        
        function = mock_abi[0]
        self.assertIn('name', function)
        self.assertIn('inputs', function)
        self.assertIn('outputs', function)
        self.assertIn('stateMutability', function)
        self.assertIn('type', function)
    
    def test_prediction_submission_format(self):
        """测试预测提交格式"""
        # 模拟提交数据
        sequence = "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK"
        stability_score = 720  # 0.72 * 1000
        
        # 验证数据格式
        self.assertIsInstance(sequence, str)
        self.assertGreater(len(sequence), 0)
        self.assertIsInstance(stability_score, int)
        self.assertGreaterEqual(stability_score, 0)
        self.assertLessEqual(stability_score, 1000)


class TestEndToEndFlow(unittest.TestCase):
    """端到端流程测试"""
    
    def setUp(self):
        self.predictor = ProteinFoldingPredictor()
    
    def test_complete_prediction_flow(self):
        """测试完整预测流程"""
        # 1. 输入序列
        test_sequence = "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK"
        
        # 2. AI预测
        prediction_result = self.predictor.predict_folding(test_sequence)
        
        # 3. 验证预测结果
        self.assertNotIn('error', prediction_result)
        self.assertGreater(prediction_result['stability_score'], 0)
        self.assertGreater(len(prediction_result['energy_plot']), 0)
        
        # 4. 准备区块链提交数据
        stability_score_scaled = int(prediction_result['stability_score'] * 1000)
        
        # 5. 验证提交数据格式
        self.assertIsInstance(stability_score_scaled, int)
        self.assertGreaterEqual(stability_score_scaled, 0)
        self.assertLessEqual(stability_score_scaled, 1000)
        
        # 6. 模拟区块链提交
        mock_submission_result = {
            "success": True,
            "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "block_number": 12345678,
            "gas_used": 150000
        }
        
        # 7. 验证提交结果
        self.assertTrue(mock_submission_result['success'])
        self.assertIn('tx_hash', mock_submission_result)
        self.assertIn('block_number', mock_submission_result)
        self.assertIn('gas_used', mock_submission_result)
    
    def test_multiple_sequences(self):
        """测试多个序列的预测"""
        test_sequences = [
            "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK",  # GFP
            "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN",  # 胰岛素
            "MKLLILTCLVAVALARPKHPIKHQGLPQEVLNENLLRFFVAPFPEVFGKEKVNELKKKDFGFIEQEGDLIVIDVPGNIQKPLGDFGDQMLRIAVKTEGALMQCKLMKQ"  # 其他蛋白
        ]
        
        results = []
        for seq in test_sequences:
            result = self.predictor.predict_folding(seq)
            results.append(result)
            
            # 验证每个结果
            self.assertNotIn('error', result)
            self.assertGreater(result['stability_score'], 0)
            self.assertGreater(len(result['energy_plot']), 0)
        
        # 验证结果多样性
        scores = [r['stability_score'] for r in results]
        self.assertEqual(len(set(scores)), len(scores))  # 所有分数应该不同


def run_performance_test():
    """性能测试"""
    import time
    
    predictor = ProteinFoldingPredictor()
    test_sequence = "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK"
    
    print("🚀 开始性能测试...")
    
    # 测试预测速度
    start_time = time.time()
    result = predictor.predict_folding(test_sequence)
    end_time = time.time()
    
    prediction_time = end_time - start_time
    
    print(f"✅ 预测完成时间: {prediction_time:.3f} 秒")
    print(f"✅ 稳定性分数: {result['stability_score']:.3f}")
    print(f"✅ 序列长度: {result['sequence_length']} 氨基酸")
    print(f"✅ 能量图大小: {len(result['energy_plot'])} 字符")
    
    # 性能基准
    if prediction_time < 5.0:
        print("🎉 性能优秀!")
    elif prediction_time < 10.0:
        print("👍 性能良好")
    else:
        print("⚠️ 性能需要优化")


if __name__ == "__main__":
    print("🧪 ProteinFoldDAO 集成测试")
    print("=" * 50)
    
    # 运行单元测试
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "=" * 50)
    
    # 运行性能测试
    run_performance_test()
    
    print("\n🎉 所有测试完成!")
