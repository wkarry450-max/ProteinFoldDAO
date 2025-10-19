#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的蛋白质数据库管理器
使用更简单的API调用方式
"""

import requests
import sqlite3
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import os

@dataclass
class ProteinInfo:
    """蛋白质信息数据类"""
    uniprot_id: str
    name: str
    sequence: str
    organism: str
    function: str
    length: int
    molecular_weight: float
    pdb_ids: List[str]
    alphafold_id: Optional[str]
    confidence_score: Optional[float]
    last_updated: datetime

class SimpleProteinDatabaseManager:
    """简化的蛋白质数据库管理器"""
    
    def __init__(self, cache_db_path: str = "protein_cache.db"):
        self.cache_db_path = cache_db_path
        self.uniprot_base_url = "https://rest.uniprot.org"
        
        # 初始化本地缓存数据库
        self._init_cache_database()
    
    def _init_cache_database(self):
        """初始化本地缓存数据库"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        # 创建蛋白质信息表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS proteins (
            uniprot_id TEXT PRIMARY KEY,
            name TEXT,
            sequence TEXT,
            organism TEXT,
            function TEXT,
            length INTEGER,
            molecular_weight REAL,
            pdb_ids TEXT,
            alphafold_id TEXT,
            confidence_score REAL,
            last_updated TIMESTAMP,
            cache_expiry TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def search_protein_by_name(self, name: str, organism: str = None) -> List[ProteinInfo]: # type: ignore
        """根据蛋白质名称搜索"""
        # 先检查本地缓存
        cached_results = self._get_cached_proteins(name, organism)
        if cached_results:
            return cached_results
        
        # 从UniProt搜索
        uniprot_results = self._search_uniprot_simple(name, organism)
        
        # 缓存结果
        for protein in uniprot_results:
            self._cache_protein(protein)
        
        return uniprot_results
    
    def get_protein_by_uniprot_id(self, uniprot_id: str) -> Optional[ProteinInfo]:
        """根据UniProt ID获取蛋白质信息"""
        # 检查缓存
        cached = self._get_cached_protein_by_id(uniprot_id)
        if cached and not self._is_cache_expired(cached.last_updated):
            return cached
        
        # 从UniProt获取详细信息
        protein_info = self._fetch_uniprot_details_simple(uniprot_id)
        if protein_info:
            self._cache_protein(protein_info)
        
        return protein_info
    
    def _search_uniprot_simple(self, name: str, organism: str = None) -> List[ProteinInfo]: # type: ignore
        """简化的UniProt搜索"""
        # 使用更简单的搜索方式
        query = name
        if organism and organism != "全部":
            query += f" {organism}"
        
        params = {
            'query': query,
            'format': 'json',
            'size': 20
        }
        
        try:
            response = requests.get(f"{self.uniprot_base_url}/uniprotkb/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            proteins = []
            for result in data.get('results', []):
                # 提取基本信息
                accession = result.get('primaryAccession', '')
                protein_desc = result.get('proteinDescription', {})
                recommended_name = protein_desc.get('recommendedName', {})
                full_name = recommended_name.get('fullName', {})
                protein_name = full_name.get('value', 'Unknown')
                
                sequence_info = result.get('sequence', {})
                sequence = sequence_info.get('value', '')
                length = sequence_info.get('length', 0)
                
                organism_info = result.get('organism', {})
                organism_name = organism_info.get('scientificName', 'Unknown')
                
                mass = result.get('mass', 0)
                
                protein = ProteinInfo(
                    uniprot_id=accession,
                    name=protein_name,
                    sequence=sequence,
                    organism=organism_name,
                    function=protein_name,
                    length=length,
                    molecular_weight=mass,
                    pdb_ids=[],
                    alphafold_id=None,
                    confidence_score=None,
                    last_updated=datetime.now()
                )
                proteins.append(protein)
            
            return proteins
        
        except requests.RequestException as e:
            print(f"UniProt搜索错误: {e}")
            return []
    
    def _fetch_uniprot_details_simple(self, uniprot_id: str) -> Optional[ProteinInfo]:
        """简化的UniProt详情获取"""
        try:
            response = requests.get(f"{self.uniprot_base_url}/uniprotkb/{uniprot_id}")
            response.raise_for_status()
            data = response.json()
            
            # 提取基本信息
            accession = data.get('primaryAccession', '')
            protein_desc = data.get('proteinDescription', {})
            recommended_name = protein_desc.get('recommendedName', {})
            full_name = recommended_name.get('fullName', {})
            protein_name = full_name.get('value', 'Unknown')
            
            sequence_info = data.get('sequence', {})
            sequence = sequence_info.get('value', '')
            length = sequence_info.get('length', 0)
            
            organism_info = data.get('organism', {})
            organism_name = organism_info.get('scientificName', 'Unknown')
            
            mass = data.get('mass', 0)
            
            # 提取PDB IDs
            pdb_ids = []
            cross_refs = data.get('uniProtKBCrossReferences', [])
            for ref in cross_refs:
                if ref.get('database') == 'PDB':
                    pdb_ids.append(ref.get('id'))
            
            # 提取AlphaFold ID
            alphafold_id = None
            for ref in cross_refs:
                if ref.get('database') == 'AlphaFoldDB':
                    alphafold_id = ref.get('id')
                    break
            
            protein = ProteinInfo(
                uniprot_id=accession,
                name=protein_name,
                sequence=sequence,
                organism=organism_name,
                function=protein_name,
                length=length,
                molecular_weight=mass,
                pdb_ids=pdb_ids,
                alphafold_id=alphafold_id,
                confidence_score=None,
                last_updated=datetime.now()
            )
            
            return protein
        
        except requests.RequestException as e:
            print(f"UniProt详情获取错误: {e}")
            return None
    
    def get_popular_proteins(self) -> List[ProteinInfo]:
        """获取热门蛋白质列表"""
        # 使用已知的UniProt IDs
        popular_uniprot_ids = [
            "P01308",  # Insulin
            "P04637",  # TP53
            "P15056",  # BRAF
            "P42345",  # MTOR
            "P31749",  # AKT1
        ]
        
        proteins = []
        for uniprot_id in popular_uniprot_ids:
            protein = self.get_protein_by_uniprot_id(uniprot_id)
            if protein:
                proteins.append(protein)
        
        return proteins
    
    def _cache_protein(self, protein: ProteinInfo):
        """缓存蛋白质信息"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO proteins 
        (uniprot_id, name, sequence, organism, function, length, molecular_weight, 
         pdb_ids, alphafold_id, confidence_score, last_updated, cache_expiry)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            protein.uniprot_id,
            protein.name,
            protein.sequence,
            protein.organism,
            protein.function,
            protein.length,
            protein.molecular_weight,
            json.dumps(protein.pdb_ids),
            protein.alphafold_id,
            protein.confidence_score,
            protein.last_updated,
            datetime.now().timestamp() + 86400  # 24小时过期
        ))
        
        conn.commit()
        conn.close()
    
    def _get_cached_proteins(self, name: str, organism: str = None) -> List[ProteinInfo]: # type: ignore
        """从缓存获取蛋白质"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM proteins WHERE name LIKE ?"
        params = [f"%{name}%"]
        
        if organism and organism != "全部":
            query += " AND organism LIKE ?"
            params.append(f"%{organism}%")
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        proteins = []
        for row in results:
            if not self._is_cache_expired(datetime.fromtimestamp(row[11])):
                protein = self._row_to_protein(row)
                proteins.append(protein)
        
        return proteins
    
    def _get_cached_protein_by_id(self, uniprot_id: str) -> Optional[ProteinInfo]:
        """根据ID从缓存获取蛋白质"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM proteins WHERE uniprot_id = ?", (uniprot_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row and not self._is_cache_expired(datetime.fromtimestamp(row[11])):
            return self._row_to_protein(row)
        
        return None
    
    def _row_to_protein(self, row) -> ProteinInfo:
        """将数据库行转换为ProteinInfo对象"""
        # 安全处理时间戳
        try:
            if isinstance(row[10], (int, float)):
                last_updated = datetime.fromtimestamp(row[10])
            else:
                last_updated = datetime.now()
        except:
            last_updated = datetime.now()
        
        return ProteinInfo(
            uniprot_id=row[0] or "",
            name=row[1] or "",
            sequence=row[2] or "",
            organism=row[3] or "",
            function=row[4] or "",
            length=row[5] or 0,
            molecular_weight=row[6] or 0.0,
            pdb_ids=json.loads(row[7]) if row[7] else [],
            alphafold_id=row[8],
            confidence_score=row[9],
            last_updated=last_updated
        )
    
    def _is_cache_expired(self, cache_time: datetime) -> bool:
        """检查缓存是否过期"""
        return (datetime.now() - cache_time).days > 1

# 使用示例
if __name__ == "__main__":
    db_manager = SimpleProteinDatabaseManager()
    
    # 搜索蛋白质
    results = db_manager.search_protein_by_name("insulin")
    print(f"找到 {len(results)} 个胰岛素相关蛋白质")
    
    for protein in results[:3]:
        print(f"- {protein.name} ({protein.uniprot_id})")
        print(f"  序列长度: {protein.length}")
        print(f"  分子量: {protein.molecular_weight}")
        print(f"  生物体: {protein.organism}")
        print()
