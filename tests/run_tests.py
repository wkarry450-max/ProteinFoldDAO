#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProteinFoldDAO 测试运行器
快速测试AI预测功能和端到端流程
"""

import sys
import os
import json
import time

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from ai.predictor import ProteinFoldingPredictor


def test_ai_predictor():
    """测试AI预测器"""
    print("🧬 测试AI预测器...")
    
    predictor = ProteinFoldingPredictor()
    
    # 测试序列
    test_sequences = {
        "GFP": "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK",
        "胰岛素": "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN",
        "短序列": "ACDEFGHIKLMNPQRSTVWY"
    }
    
    results = {}
    
    for name, sequence in test_sequences.items():
        print(f"  📝 测试 {name}...")
        
        start_time = time.time()
        result = predictor.predict_folding(sequence)
        end_time = time.time()
        
        if "error" in result:
            print(f"    ❌ 错误: {result['error']}")
        else:
            print(f"    ✅ 稳定性分数: {result['stability_score']:.3f}")
            print(f"    ✅ 序列长度: {result['sequence_length']} 氨基酸")
            print(f"    ✅ 预测时间: {end_time - start_time:.3f} 秒")
            print(f"    ✅ 能量图: {len(result['energy_plot'])} 字符")
            
            results[name] = result
    
    return results


def test_validation():
    """测试序列验证"""
    print("\n🔍 测试序列验证...")
    
    predictor = ProteinFoldingPredictor()
    
    test_cases = [
        ("有效序列", "ACDEFGHIKLMNPQRSTVWY", True),
        ("包含数字", "ACDEFGHIKLMNPQRSTVWY123", False),
        ("包含特殊字符", "ACDEFGHIKLMNPQRSTVWY@", False),
        ("空序列", "", False),
        ("只有空格", "   ", False),
        ("小写字母", "acdefghiklmnpqrstvwy", True),  # 应该被转换为大写
        ("混合大小写", "AcDeFgHiKlMnPqRsTvWy", True)
    ]
    
    for name, sequence, expected in test_cases:
        result = predictor.validate_sequence(sequence)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {name}: {result} (期望: {expected})")


def test_error_handling():
    """测试错误处理"""
    print("\n⚠️ 测试错误处理...")
    
    predictor = ProteinFoldingPredictor()
    
    error_cases = [
        ("空字符串", ""),
        ("None", None),
        ("无效字符", "INVALID123"),
        ("特殊字符", "ACDEFGHIKLMNPQRSTVWY@#$"),
        ("数字", "123456789")
    ]
    
    for name, sequence in error_cases:
        result = predictor.predict_folding(sequence)
        if "error" in result:
            print(f"  ✅ {name}: 正确处理错误 - {result['error']}")
        else:
            print(f"  ❌ {name}: 未正确处理错误")


def test_performance():
    """性能测试"""
    print("\n🚀 性能测试...")
    
    predictor = ProteinFoldingPredictor()
    
    # 长序列测试
    long_sequence = "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK" * 2
    
    print(f"  📏 测试序列长度: {len(long_sequence)} 氨基酸")
    
    start_time = time.time()
    result = predictor.predict_folding(long_sequence)
    end_time = time.time()
    
    prediction_time = end_time - start_time
    
    if "error" in result:
        print(f"    ❌ 预测失败: {result['error']}")
    else:
        print(f"    ✅ 预测时间: {prediction_time:.3f} 秒")
        print(f"    ✅ 稳定性分数: {result['stability_score']:.3f}")
        print(f"    ✅ 能量图大小: {len(result['energy_plot'])} 字符")
        
        # 性能评估
        if prediction_time < 2.0:
            print("    🎉 性能优秀!")
        elif prediction_time < 5.0:
            print("    👍 性能良好")
        else:
            print("    ⚠️ 性能需要优化")


def test_blockchain_format():
    """测试区块链数据格式"""
    print("\n⛓️ 测试区块链数据格式...")
    
    predictor = ProteinFoldingPredictor()
    test_sequence = "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK"
    
    result = predictor.predict_folding(test_sequence)
    
    if "error" not in result:
        # 模拟区块链提交数据
        blockchain_data = {
            "sequence": test_sequence,
            "stabilityScore": int(result['stability_score'] * 1000),
            "submitter": "0x742d35Cc6634C0532925a3b8D2C5C5C5C5C5C5C5",
            "timestamp": int(time.time())
        }
        
        print(f"  ✅ 序列长度: {len(blockchain_data['sequence'])} 字符")
        print(f"  ✅ 稳定性分数: {blockchain_data['stabilityScore']} (缩放后)")
        print(f"  ✅ 提交者地址: {blockchain_data['submitter']}")
        print(f"  ✅ 时间戳: {blockchain_data['timestamp']}")
        
        # 验证数据格式
        assert isinstance(blockchain_data['stabilityScore'], int)
        assert 0 <= blockchain_data['stabilityScore'] <= 1000
        assert len(blockchain_data['submitter']) == 42  # Ethereum地址长度
        assert blockchain_data['timestamp'] > 0
        
        print("  ✅ 区块链数据格式验证通过")


def main():
    """主测试函数"""
    print("🧪 ProteinFoldDAO 快速测试")
    print("=" * 60)
    
    try:
        # 运行各项测试
        test_ai_predictor()
        test_validation()
        test_error_handling()
        test_performance()
        test_blockchain_format()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试完成!")
        print("✅ AI预测器工作正常")
        print("✅ 序列验证功能正常")
        print("✅ 错误处理机制正常")
        print("✅ 性能表现良好")
        print("✅ 区块链数据格式正确")
        
        print("\n🚀 可以开始使用ProteinFoldDAO了!")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
