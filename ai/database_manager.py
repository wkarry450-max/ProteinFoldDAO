#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蛋白质数据库集成模块
支持UniProt、PDB、AlphaFold等主要数据库
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

class ProteinDatabaseManager:
    """蛋白质数据库管理器"""
    
    def __init__(self, cache_db_path: str = "protein_cache.db"):
        self.cache_db_path = cache_db_path
        self.uniprot_base_url = "https://rest.uniprot.org"
        self.pdb_base_url = "https://data.rcsb.org/rest/v1"
        self.alphafold_base_url = "https://alphafold.ebi.ac.uk/api"
        
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
        
        # 创建搜索索引
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_name ON proteins(name)
        ''')
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_organism ON proteins(organism)
        ''')
        
        conn.commit()
        conn.close()
    
    def search_protein_by_name(self, name: str, organism: str = None) -> List[ProteinInfo]:  # pyright: ignore[reportArgumentType]
        """根据蛋白质名称搜索"""
        # 先检查本地缓存
        cached_results = self._get_cached_proteins(name, organism)
        if cached_results:
            return cached_results
        
        # 从UniProt搜索
        uniprot_results = self._search_uniprot(name, organism)
        
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
        protein_info = self._fetch_uniprot_details(uniprot_id)
        if protein_info:
            self._cache_protein(protein_info)
        
        return protein_info
    
    def get_protein_structure(self, uniprot_id: str) -> Optional[Dict]:
        """获取蛋白质3D结构信息"""
        protein_info = self.get_protein_by_uniprot_id(uniprot_id)
        if not protein_info:
            return None
        
        # 尝试从AlphaFold获取结构
        if protein_info.alphafold_id:
            return self._fetch_alphafold_structure(protein_info.alphafold_id)
        
        # 尝试从PDB获取结构
        if protein_info.pdb_ids:
            return self._fetch_pdb_structure(protein_info.pdb_ids[0])
        
        return None
    
    def _search_uniprot(self, name: str, organism: str = None) -> List[ProteinInfo]:  # pyright: ignore[reportArgumentType]
        """从UniProt搜索蛋白质"""
        query = f"name:{name}"
        if organism:
            query += f" AND organism:{organism}"
        
        params = {
            'query': query,
            'format': 'json',
            'size': 50
        }
        
        try:
            response = requests.get(f"{self.uniprot_base_url}/uniprotkb/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            proteins = []
            for result in data.get('results', []):
                protein = ProteinInfo(
                    uniprot_id=result.get('primaryAccession', ''),
                    name=result.get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value', ''),
                    sequence=result.get('sequence', {}).get('value', ''),
                    organism=result.get('organism', {}).get('scientificName', ''),
                    function=result.get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value', ''),
                    length=result.get('sequence', {}).get('length', 0),
                    molecular_weight=result.get('mass', 0),
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
    
    def _fetch_uniprot_details(self, uniprot_id: str) -> Optional[ProteinInfo]:
        """获取UniProt详细信息"""
        params = {
            'format': 'json'
        }
        
        try:
            response = requests.get(f"{self.uniprot_base_url}/uniprotkb/{uniprot_id}", params=params)
            response.raise_for_status()
            data = response.json()
            
            # 提取PDB IDs
            pdb_ids = []
            for db_ref in data.get('uniProtKBCrossReferences', []):
                if db_ref.get('database') == 'PDB':
                    pdb_ids.append(db_ref.get('id'))
            
            # 提取AlphaFold ID
            alphafold_id = None
            for db_ref in data.get('uniProtKBCrossReferences', []):
                if db_ref.get('database') == 'AlphaFoldDB':
                    alphafold_id = db_ref.get('id')
                    break
            
            protein = ProteinInfo(
                uniprot_id=data.get('primaryAccession', ''),
                name=data.get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value', ''),
                sequence=data.get('sequence', {}).get('value', ''),
                organism=data.get('organism', {}).get('scientificName', ''),
                function=data.get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value', ''),
                length=data.get('sequence', {}).get('length', 0),
                molecular_weight=data.get('mass', 0),
                pdb_ids=pdb_ids,
                alphafold_id=alphafold_id,
                confidence_score=None,
                last_updated=datetime.now()
            )
            
            return protein
        
        except requests.RequestException as e:
            print(f"UniProt详情获取错误: {e}")
            return None
    
    def _fetch_alphafold_structure(self, alphafold_id: str) -> Optional[Dict]:
        """获取AlphaFold结构信息"""
        try:
            response = requests.get(f"{self.alphafold_base_url}/prediction/{alphafold_id}")
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            print(f"AlphaFold结构获取错误: {e}")
            return None
    
    def _fetch_pdb_structure(self, pdb_id: str) -> Optional[Dict]:
        """获取PDB结构信息"""
        try:
            response = requests.get(f"{self.pdb_base_url}/core/entry/{pdb_id}")
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            print(f"PDB结构获取错误: {e}")
            return None
    
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
    
    def _get_cached_proteins(self, name: str, organism: str = None) -> List[ProteinInfo]:  # pyright: ignore[reportArgumentType]
        """从缓存获取蛋白质"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM proteins WHERE name LIKE ?"
        params = [f"%{name}%"]
        
        if organism:
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
        return ProteinInfo(
            uniprot_id=row[0],
            name=row[1],
            sequence=row[2],
            organism=row[3],
            function=row[4],
            length=row[5],
            molecular_weight=row[6],
            pdb_ids=json.loads(row[7]) if row[7] else [],
            alphafold_id=row[8],
            confidence_score=row[9],
            last_updated=datetime.fromtimestamp(row[10])
        )
    
    def _is_cache_expired(self, cache_time: datetime) -> bool:
        """检查缓存是否过期"""
        return (datetime.now() - cache_time).days > 1
    
    def get_popular_proteins(self) -> List[ProteinInfo]:
        """获取热门蛋白质列表"""
        popular_uniprot_ids = [
            "P00520",  # ABL1
            "P04637",  # TP53
            "P15056",  # BRAF
            "P42345",  # MTOR
            "P31749",  # AKT1
            "P06493",  # CDK1
            "P24941",  # CDK2
            "P11388",  # TOP2A
            "P10275",  # AR
            "P03372"   # ESR1
        ]
        
        proteins = []
        for uniprot_id in popular_uniprot_ids:
            protein = self.get_protein_by_uniprot_id(uniprot_id)
            if protein:
                proteins.append(protein)
        
        return proteins

# 使用示例
if __name__ == "__main__":
    db_manager = ProteinDatabaseManager()
    
    # 搜索蛋白质
    results = db_manager.search_protein_by_name("insulin", "Homo sapiens")
    print(f"找到 {len(results)} 个胰岛素相关蛋白质")
    
    for protein in results[:3]:
        print(f"- {protein.name} ({protein.uniprot_id})")
        print(f"  序列长度: {protein.length}")
        print(f"  分子量: {protein.molecular_weight}")
        print(f"  生物体: {protein.organism}")
        print()
