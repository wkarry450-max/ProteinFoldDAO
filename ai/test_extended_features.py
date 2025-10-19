#!/usr/bin/env python3
"""
测试扩展的蛋白质特性分析功能
"""

from predictor import ProteinFoldingPredictor

def test_extended_features():
    """测试扩展的蛋白质特性分析"""
    predictor = ProteinFoldingPredictor()
    
    # 测试GFP序列
    test_sequence = 'MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK'
    
    print('测试扩展的蛋白质特性分析')
    print('=' * 50)
    
    result = predictor.predict_folding(test_sequence)
    
    print(f'基础信息:')
    print(f'  序列长度: {result["sequence_length"]} 氨基酸')
    print(f'  稳定性分数: {result["stability_score"]}')
    print(f'  分子量: {result["molecular_weight"]} Da')
    print(f'  等电点: {result["isoelectric_point"]}')
    print(f'  平均体积: {result["average_volume"]} A3')
    print(f'  柔性指数: {result["flexibility_index"]}')
    
    print(f'\n氨基酸类别分布:')
    for category, data in result['amino_acid_distribution'].items():
        print(f'  {category}: {data["percentage"]:.1f}% ({data["count"]}个)')
    
    print(f'\n二级结构倾向性:')
    ss = result['secondary_structure_tendency']
    print(f'  α-螺旋: {ss["helix_tendency"]:.1f}%')
    print(f'  β-折叠: {ss["sheet_tendency"]:.1f}%')
    print(f'  转角: {ss["turn_tendency"]:.1f}%')
    
    print(f'\n热稳定性分析:')
    thermo = result['thermostability_indicators']
    print(f'  热稳定性评分: {thermo["thermostability_score"]:.3f}')
    print(f'  半胱氨酸含量: {thermo["cysteine_content"]:.2f}%')
    print(f'  潜在二硫键: {thermo["potential_disulfide_bonds"]}')
    
    print(f'\n无序倾向性: {result["disorder_tendency"]:.3f}')
    
    print(f'\n氨基酸组成 (前10个):')
    aa_comp = result['amino_acid_composition']
    sorted_aa = sorted(aa_comp.items(), key=lambda x: x[1]['percentage'], reverse=True)
    for aa, data in sorted_aa[:10]:
        print(f'  {aa}: {data["percentage"]:.2f}% ({data["count"]}个)')

if __name__ == "__main__":
    test_extended_features()
