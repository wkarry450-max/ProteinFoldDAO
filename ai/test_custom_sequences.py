#!/usr/bin/env python3
"""
测试自定义序列处理
"""

from predictor import ProteinFoldingPredictor

def test_custom_sequences():
    """测试各种自定义序列"""
    predictor = ProteinFoldingPredictor()
    
    # 测试各种自定义序列
    test_sequences = [
        ('MKWVTFISLLFLFSSAYS', '简单序列'),
        ('MKWVTFISLLFLFSSAYS123', '包含数字'),
        ('MKWVTFISLLFLFSSAYS@#$', '包含特殊字符'),
        ('mkwtfisllflfssays', '小写'),
        ('MkWVtFiSlLfLfSsAyS', '混合大小写'),
        ('MKWVTFISLLFLFSSAYS\nMKWVTFISLLFLFSSAYS', '包含换行'),
        ('MKWVTFISLLFLFSSAYS MKWVTFISLLFLFSSAYS', '包含空格'),
        ('ACDEFGHIKLMNPQRSTVWY', '标准20种氨基酸'),
        ('ACDEFGHIKLMNPQRSTVWYZ', '包含无效氨基酸Z'),
        ('ACDEFGHIKLMNPQRSTVWY123456', '包含数字'),
        ('ACDEFGHIKLMNPQRSTVWY@#$%', '包含特殊字符'),
        ('', '空序列'),
        ('   ', '只有空格'),
        ('ABC', '太短序列'),
    ]
    
    print("🧬 测试自定义序列处理")
    print("=" * 50)
    
    for i, (seq, desc) in enumerate(test_sequences):
        print(f"\n测试 {i+1}: {desc}")
        print(f"输入: {repr(seq)}")
        
        # 先测试验证函数
        is_valid, error_msg = predictor.validate_sequence(seq)
        print(f"验证结果: {is_valid}")
        if not is_valid:
            print(f"错误信息: {error_msg}")
        
        # 测试完整预测
        result = predictor.predict_folding(seq)
        if 'error' in result:
            print(f"❌ 预测失败: {result['error']}")
        else:
            print(f"✅ 预测成功:")
            print(f"  长度: {result['sequence_length']}")
            print(f"  稳定性: {result['stability_score']}")
            print(f"  分子量: {result['molecular_weight']}")
            print(f"  疏水性: {result['hydrophobicity']}")
            print(f"  电荷平衡: {result['charge_balance']}")
    
    print("\n" + "=" * 50)
    print("🎉 自定义序列测试完成!")

if __name__ == "__main__":
    test_custom_sequences()

