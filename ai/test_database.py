#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蛋白质数据库功能测试脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.database_manager import ProteinDatabaseManager

def test_database_functionality():
    """测试数据库功能"""
    print("ProteinFoldDAO 数据库功能测试")
    print("=" * 50)
    
    # 创建数据库管理器
    db_manager = ProteinDatabaseManager()
    
    # 测试1: 搜索胰岛素
    print("\n1. 搜索胰岛素...")
    results = db_manager.search_protein_by_name("insulin", "Homo sapiens")
    print(f"找到 {len(results)} 个结果")
    
    if results:
        protein = results[0]
        print(f"  第一个结果: {protein.name}")
        print(f"  UniProt ID: {protein.uniprot_id}")
        print(f"  序列长度: {protein.length}")
        print(f"  分子量: {protein.molecular_weight:.0f} Da")
        print(f"  生物体: {protein.organism}")
    
    # 测试2: 获取热门蛋白质
    print("\n2. 获取热门蛋白质...")
    popular = db_manager.get_popular_proteins()
    print(f"加载了 {len(popular)} 个热门蛋白质")
    
    for i, protein in enumerate(popular[:3]):
        print(f"  {i+1}. {protein.name} ({protein.uniprot_id})")
        print(f"     序列长度: {protein.length}, 分子量: {protein.molecular_weight:.0f} Da")
    
    # 测试3: 根据ID获取详细信息
    if results:
        print("\n3. 获取详细信息...")
        uniprot_id = results[0].uniprot_id
        detailed = db_manager.get_protein_by_uniprot_id(uniprot_id)
        
        if detailed:
            print(f"  蛋白质名称: {detailed.name}")
            print(f"  PDB结构数: {len(detailed.pdb_ids)}")
            print(f"  AlphaFold ID: {detailed.alphafold_id}")
            print(f"  功能描述: {detailed.function[:100]}...")
    
    print("\n数据库功能测试完成!")

if __name__ == "__main__":
    test_database_functionality()
