#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProteinFoldDAO AI预测模块
核心功能：蛋白序列分析、稳定性评分、能量路径可视化
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import base64
import io
import json
import random
from typing import Dict, Tuple, Any
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from Bio.SeqUtils import molecular_weight


class ProteinFoldingPredictor:
    """蛋白折叠预测器"""
    
    def __init__(self):
        # 氨基酸疏水性指数 (Kyte-Doolittle scale)
        self.hydrophobicity_scale = {
            'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
            'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
            'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
            'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
        }
        
        # 氨基酸电荷性质
        self.charged_aa = {'R': 1, 'K': 1, 'D': -1, 'E': -1, 'H': 0.5}
        
        # 氨基酸分类
        self.aa_categories = {
            'polar': set('NQSTY'),
            'nonpolar': set('AGILMFPWV'),
            'acidic': set('DE'),
            'basic': set('RHK'),
            'aromatic': set('FWY'),
            'sulfur': set('CM'),
            'small': set('AGSV'),
            'large': set('FWY')
        }
        
        # 氨基酸体积 (Å³)
        self.aa_volume = {
            'A': 88.6, 'R': 173.4, 'N': 114.1, 'D': 111.1, 'C': 108.5,
            'Q': 143.8, 'E': 138.4, 'G': 60.1, 'H': 153.2, 'I': 166.7,
            'L': 166.7, 'K': 168.6, 'M': 162.9, 'F': 189.9, 'P': 112.7,
            'S': 89.0, 'T': 116.1, 'W': 227.8, 'Y': 193.6, 'V': 140.0
        }
        
        # 氨基酸柔性指数
        self.flexibility_index = {
            'A': 0.360, 'R': 0.529, 'N': 0.463, 'D': 0.511, 'C': 0.346,
            'Q': 0.493, 'E': 0.497, 'G': 0.544, 'H': 0.323, 'I': 0.462,
            'L': 0.365, 'K': 0.466, 'M': 0.295, 'F': 0.314, 'P': 0.509,
            'S': 0.507, 'T': 0.444, 'W': 0.305, 'Y': 0.420, 'V': 0.386
        }
        
        # 氨基酸等电点
        self.isoelectric_points = {
            'A': 6.0, 'R': 10.8, 'N': 5.4, 'D': 2.8, 'C': 5.1,
            'Q': 5.7, 'E': 3.2, 'G': 6.0, 'H': 7.6, 'I': 6.0,
            'L': 6.0, 'K': 9.7, 'M': 5.7, 'F': 5.5, 'P': 6.3,
            'S': 5.7, 'T': 5.6, 'W': 5.9, 'Y': 5.7, 'V': 6.0
        }
    
    def clean_sequence(self, sequence: str) -> str:
        """清理序列：移除非字母字符，转换为大写"""
        if not sequence:
            return ""
        return ''.join(c.upper() for c in sequence if c.isalpha())
        
    def validate_sequence(self, sequence: str) -> tuple[bool, str]:
        """验证蛋白序列格式，返回(是否有效, 错误信息)"""
        if not sequence or not sequence.strip():
            return False, "序列不能为空"
        
        # 清理序列：移除换行符、空格、数字等
        sequence_clean = self.clean_sequence(sequence)
        
        if not sequence_clean:  # 清理后仍为空
            return False, "序列只包含非字母字符"
        
        # 检查长度
        if len(sequence_clean) < 5:
            return False, f"序列太短（{len(sequence_clean)}个字符），至少需要5个氨基酸"
        
        if len(sequence_clean) > 1000:
            return False, f"序列太长（{len(sequence_clean)}个字符），最多支持1000个氨基酸"
            
        # 检查是否只包含有效氨基酸
        valid_aa = set('ACDEFGHIKLMNPQRSTVWY')
        invalid_chars = set(sequence_clean) - valid_aa
        if invalid_chars:
            return False, f"序列包含无效字符: {', '.join(sorted(invalid_chars))}"
        
        return True, ""
    
    def calculate_hydrophobicity(self, sequence: str) -> float:
        """计算序列平均疏水性"""
        sequence_clean = self.clean_sequence(sequence)
        hydrophobicity_values = [self.hydrophobicity_scale.get(aa, 0) for aa in sequence_clean]
        return np.mean(hydrophobicity_values) if hydrophobicity_values else 0 # type: ignore
    
    def calculate_charge_balance(self, sequence: str) -> float:
        """计算电荷平衡"""
        sequence_clean = self.clean_sequence(sequence)
        charges = [self.charged_aa.get(aa, 0) for aa in sequence_clean]
        net_charge = sum(charges)
        return abs(net_charge) / len(sequence_clean) if sequence_clean else 0
    
    def calculate_stability_score(self, sequence: str) -> float:
        """计算蛋白折叠稳定性分数 (0-1, 高=稳定)"""
        is_valid, error_msg = self.validate_sequence(sequence)
        if not is_valid:
            return 0.0
        
        sequence_clean = self.clean_sequence(sequence)
        
        # 基础指标
        length = len(sequence_clean)
        hydrophobicity = self.calculate_hydrophobicity(sequence_clean)
        charge_balance = self.calculate_charge_balance(sequence_clean)
        
        # 使用BioPython分析
        try:
            analysis = ProteinAnalysis(sequence_clean)
            instability_index = analysis.instability_index()
            aromaticity = analysis.aromaticity()
            molecular_weight_val = molecular_weight(sequence_clean)
        except:
            instability_index = 50.0  # 默认值
            aromaticity = 0.1
            molecular_weight_val = length * 110  # 平均分子量
        
        # 稳定性评分算法
        # 1. 长度因子 (适中长度更稳定)
        length_factor = 1.0 - abs(length - 200) / 1000 if length > 0 else 0
        
        # 2. 疏水性因子 (中等疏水性更稳定)
        hydrophobicity_factor = 1.0 - abs(hydrophobicity) / 5.0
        
        # 3. 电荷平衡因子
        charge_factor = 1.0 - charge_balance
        
        # 4. 不稳定性指数因子
        instability_factor = max(0, 1.0 - instability_index / 100.0)
        
        # 5. 芳香性因子
        aromaticity_factor = min(1.0, aromaticity * 2)
        
        # 6. 分子量因子
        mw_factor = 1.0 - abs(molecular_weight_val - 25000) / 100000
        
        # 加权平均
        weights = [0.2, 0.2, 0.15, 0.2, 0.1, 0.15]
        factors = [length_factor, hydrophobicity_factor, charge_factor, 
                  instability_factor, aromaticity_factor, mw_factor]
        
        stability_score = sum(w * f for w, f in zip(weights, factors))
        
        # 添加一些随机性模拟AI不确定性
        noise = random.uniform(-0.05, 0.05)
        stability_score = max(0.0, min(1.0, stability_score + noise))
        
        return round(stability_score, 3)
    
    def calculate_amino_acid_composition(self, sequence: str) -> dict:
        """计算氨基酸组成"""
        sequence_clean = self.clean_sequence(sequence)
        total = len(sequence_clean)
        
        composition = {}
        for aa in 'ACDEFGHIKLMNPQRSTVWY':
            count = sequence_clean.count(aa)
            composition[aa] = {
                'count': count,
                'percentage': round(count / total * 100, 2) if total > 0 else 0
            }
        
        return composition
    
    def calculate_aa_category_distribution(self, sequence: str) -> dict:
        """计算氨基酸类别分布"""
        sequence_clean = self.clean_sequence(sequence)
        total = len(sequence_clean)
        
        distribution = {}
        for category, aa_set in self.aa_categories.items():
            count = sum(1 for aa in sequence_clean if aa in aa_set)
            distribution[category] = {
                'count': count,
                'percentage': round(count / total * 100, 2) if total > 0 else 0
            }
        
        return distribution
    
    def calculate_average_volume(self, sequence: str) -> float:
        """计算平均体积"""
        sequence_clean = self.clean_sequence(sequence)
        volumes = [self.aa_volume.get(aa, 0) for aa in sequence_clean]
        return np.mean(volumes) if volumes else 0 # type: ignore
    
    def calculate_flexibility(self, sequence: str) -> float:
        """计算平均柔性指数"""
        sequence_clean = self.clean_sequence(sequence)
        flexibilities = [self.flexibility_index.get(aa, 0) for aa in sequence_clean]
        return np.mean(flexibilities) if flexibilities else 0 # type: ignore
    
    def calculate_isoelectric_point(self, sequence: str) -> float:
        """计算等电点"""
        sequence_clean = self.clean_sequence(sequence)
        pI_values = [self.isoelectric_points.get(aa, 6.0) for aa in sequence_clean]
        return np.mean(pI_values) if pI_values else 6.0 # type: ignore
    
    def calculate_secondary_structure_tendency(self, sequence: str) -> dict:
        """计算二级结构倾向性"""
        sequence_clean = self.clean_sequence(sequence)
        
        # 简化的二级结构倾向性评分
        helix_favoring = set('AELKMQ')
        sheet_favoring = set('VITYFW')
        turn_favoring = set('PGNDS')
        
        helix_count = sum(1 for aa in sequence_clean if aa in helix_favoring)
        sheet_count = sum(1 for aa in sequence_clean if aa in sheet_favoring)
        turn_count = sum(1 for aa in sequence_clean if aa in turn_favoring)
        total = len(sequence_clean)
        
        return {
            'helix_tendency': round(helix_count / total * 100, 2) if total > 0 else 0,
            'sheet_tendency': round(sheet_count / total * 100, 2) if total > 0 else 0,
            'turn_tendency': round(turn_count / total * 100, 2) if total > 0 else 0
        }
    
    def calculate_disorder_tendency(self, sequence: str) -> float:
        """计算无序倾向性"""
        sequence_clean = self.clean_sequence(sequence)
        
        # 基于氨基酸特性的无序倾向性评分
        disorder_favoring = {'P': 0.8, 'G': 0.6, 'S': 0.4, 'N': 0.4, 'Q': 0.4}
        order_favoring = {'C': 0.8, 'W': 0.6, 'F': 0.6, 'Y': 0.5, 'I': 0.5, 'L': 0.5, 'V': 0.5}
        
        disorder_score = sum(disorder_favoring.get(aa, 0) for aa in sequence_clean)
        order_score = sum(order_favoring.get(aa, 0) for aa in sequence_clean)
        
        total_score = disorder_score + order_score
        return round(disorder_score / total_score, 3) if total_score > 0 else 0.5
    
    def calculate_thermostability_indicators(self, sequence: str) -> dict:
        """计算热稳定性指标"""
        sequence_clean = self.clean_sequence(sequence)
        
        # 热稳定性相关氨基酸
        thermostable_aa = {'C': 2, 'W': 1.5, 'F': 1.2, 'Y': 1.1, 'I': 1.1, 'L': 1.1, 'V': 1.1}
        thermolabile_aa = {'G': 0.5, 'S': 0.7, 'N': 0.8, 'Q': 0.8, 'D': 0.8, 'E': 0.8}
        
        stable_score = sum(thermostable_aa.get(aa, 1) for aa in sequence_clean)
        labile_score = sum(thermolabile_aa.get(aa, 1) for aa in sequence_clean)
        
        # 计算Cys含量（二硫键形成能力）
        cys_count = sequence_clean.count('C')
        cys_percentage = cys_count / len(sequence_clean) * 100 if sequence_clean else 0
        
        return {
            'thermostability_score': round(stable_score / (stable_score + labile_score), 3) if (stable_score + labile_score) > 0 else 0.5,
            'cysteine_content': round(cys_percentage, 2),
            'potential_disulfide_bonds': cys_count // 2
        }
    
    def generate_energy_plot(self, sequence: str) -> str:
        """生成能量路径可视化图"""
        sequence_clean = self.clean_sequence(sequence)
        length = len(sequence_clean)
        
        # 生成模拟能量路径
        x = np.arange(min(100, length))  # 前100个氨基酸
        
        # 基于序列特征生成能量曲线
        hydrophobicity_values = [self.hydrophobicity_scale.get(aa, 0) for aa in sequence_clean[:100]]
        energy_values = []
        
        for i, hydro in enumerate(hydrophobicity_values):
            # 模拟折叠能量 (负值表示稳定)
            base_energy = -hydro * 0.5
            # 添加局部结构影响
            local_factor = np.sin(i * 0.3) * 0.2
            # 添加随机噪声
            noise = random.uniform(-0.1, 0.1)
            energy = base_energy + local_factor + noise
            energy_values.append(energy)
        
        # 创建图表
        plt.figure(figsize=(8, 4))  # 减小高度，与下面的图表保持一致
        plt.plot(x, energy_values, 'b-', linewidth=2, label='Folding Energy')
        plt.fill_between(x, energy_values, alpha=0.3, color='blue')
        
        plt.xlabel('Amino Acid Position', fontsize=10)
        plt.ylabel('Relative Energy (kcal/mol)', fontsize=10)
        plt.title('Protein Folding Energy Path', fontsize=12, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=9)
        
        # 添加稳定性区域标注
        stable_regions = np.where(np.array(energy_values) < -0.5)[0]
        if len(stable_regions) > 0:
            plt.scatter(stable_regions, [energy_values[i] for i in stable_regions], 
                       color='green', s=20, alpha=0.7, label='Stable Regions')
        
        plt.tight_layout()
        
        # 转换为base64字符串
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def predict_folding(self, sequence: str) -> Dict[str, Any]:
        """主要预测函数"""
        if not sequence or not sequence.strip():
            return {
                "error": "序列不能为空",
                "sequence_length": 0,
                "stability_score": 0.0,
                "energy_plot": ""
            }
        
        is_valid, error_msg = self.validate_sequence(sequence)
        if not is_valid:
            return {
                "error": error_msg,
                "sequence_length": 0,
                "stability_score": 0.0,
                "energy_plot": ""
            }
        
        sequence_clean = self.clean_sequence(sequence)
        
        # 计算预测结果
        stability_score = self.calculate_stability_score(sequence_clean)
        energy_plot = self.generate_energy_plot(sequence_clean)
        
        # 额外分析信息
        try:
            analysis = ProteinAnalysis(sequence_clean)
            molecular_weight_val = float(molecular_weight(sequence_clean))
            instability_index = float(analysis.instability_index())
        except:
            molecular_weight_val = float(len(sequence_clean) * 110)
            instability_index = 50.0
        
        # 计算所有蛋白质特性
        aa_composition = self.calculate_amino_acid_composition(sequence_clean)
        aa_distribution = self.calculate_aa_category_distribution(sequence_clean)
        average_volume = self.calculate_average_volume(sequence_clean)
        flexibility = self.calculate_flexibility(sequence_clean)
        isoelectric_point = self.calculate_isoelectric_point(sequence_clean)
        secondary_structure = self.calculate_secondary_structure_tendency(sequence_clean)
        disorder_tendency = self.calculate_disorder_tendency(sequence_clean)
        thermostability = self.calculate_thermostability_indicators(sequence_clean)
        
        return {
            "sequence_length": len(sequence_clean),
            "stability_score": stability_score,
            "energy_plot": energy_plot,
            "molecular_weight": round(molecular_weight_val, 2),
            "instability_index": round(instability_index, 2),
            "hydrophobicity": round(self.calculate_hydrophobicity(sequence_clean), 3),
            "charge_balance": round(self.calculate_charge_balance(sequence_clean), 3),
            
            # 新增的蛋白质特性
            "amino_acid_composition": aa_composition,
            "amino_acid_distribution": aa_distribution,
            "average_volume": round(average_volume, 2),
            "flexibility_index": round(flexibility, 3),
            "isoelectric_point": round(isoelectric_point, 2),
            "secondary_structure_tendency": secondary_structure,
            "disorder_tendency": disorder_tendency,
            "thermostability_indicators": thermostability
        }


def main():
    """测试函数"""
    predictor = ProteinFoldingPredictor()
    
    # GFP (绿色荧光蛋白) 示例序列
    gfp_sequence = """
    MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK
    """
    
    print("ProteinFoldDAO AI预测器测试")
    print("=" * 50)
    
    # 测试预测
    result = predictor.predict_folding(gfp_sequence)
    
    if "error" in result:
        print(f"错误: {result['error']}")
    else:
        print(f"序列长度: {result['sequence_length']} 氨基酸")
        print(f"稳定性分数: {result['stability_score']:.3f}")
        print(f"分子量: {result['molecular_weight']:.2f} Da")
        print(f"不稳定性指数: {result['instability_index']:.2f}")
        print(f"疏水性: {result['hydrophobicity']:.3f}")
        print(f"电荷平衡: {result['charge_balance']:.3f}")
        print(f"能量图已生成: {len(result['energy_plot'])} 字符")
        
        # 保存结果到JSON文件
        with open('prediction_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("结果已保存到 prediction_result.json")


if __name__ == "__main__":
    main()
