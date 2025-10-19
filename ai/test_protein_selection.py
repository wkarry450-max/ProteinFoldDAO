#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库选择和序列填充功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.simple_database_manager import SimpleProteinDatabaseManager

def test_protein_selection():
    """测试蛋白质选择和序列获取"""
    print("ProteinFoldDAO 数据库选择和序列填充测试")
    print("=" * 50)
    
    # 创建数据库管理器
    db_manager = SimpleProteinDatabaseManager()
    
    # 测试1: 搜索胰岛素
    print("\n1. 搜索胰岛素...")
    results = db_manager.search_protein_by_name("insulin", "Homo sapiens")
    print(f"找到 {len(results)} 个结果")
    
    if results:
        protein = results[0]
        print(f"选择的蛋白质: {protein.name}")
        print(f"UniProt ID: {protein.uniprot_id}")
        print(f"序列长度: {protein.length}")
        print(f"分子量: {protein.molecular_weight:.0f} Da")
        print(f"生物体: {protein.organism}")
        
        # 显示序列的前50个字符
        if protein.sequence:
            print(f"序列预览: {protein.sequence[:50]}...")
            print(f"完整序列长度: {len(protein.sequence)} 字符")
        else:
            print("⚠️ 序列为空")
    
    # 测试2: 获取热门蛋白质
    print("\n2. 获取热门蛋白质...")
    popular = db_manager.get_popular_proteins()
    print(f"加载了 {len(popular)} 个热门蛋白质")
    
    for i, protein in enumerate(popular[:2]):
        print(f"\n热门蛋白质 {i+1}:")
        print(f"  名称: {protein.name}")
        print(f"  UniProt ID: {protein.uniprot_id}")
        print(f"  序列长度: {protein.length}")
        if protein.sequence:
            print(f"  序列预览: {protein.sequence[:30]}...")
        else:
            print("  ⚠️ 序列为空")
    
    print("\n数据库选择和序列填充功能测试完成!")
    print("\n💡 使用说明:")
    print("1. 在Streamlit应用中搜索蛋白质")
    print("2. 点击'选择'按钮选择蛋白质")
    print("3. 切换到'AI预测'标签页")
    print("4. 查看自动填充的序列")
    print("5. 点击'开始预测'进行分析")

if __name__ == "__main__":
    test_protein_selection()
