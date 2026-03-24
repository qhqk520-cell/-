#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文献数据导入工具 - 为mini设计的批量数据处理工具
作者: ds
创建时间: 2026-03-24
目的: 帮助mini批量导入和处理佛学文献数据
"""

import json
import csv
import sqlite3
from datetime import datetime
from typing import Dict, List, Any
import os

class LiteratureDataImporter:
    """佛学文献数据导入器"""
    
    def __init__(self, db_path: str = "buddhist_literature.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """连接到数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"✅ 已连接到数据库: {self.db_path}")
        
    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            print("✅ 数据库连接已关闭")
    
    def setup_database(self):
        """设置数据库表结构（基于共享文献数据库设计）"""
        print("🔄 正在创建数据库表结构...")
        
        # 1. 文献分类表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS literature_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name VARCHAR(100) NOT NULL,
            parent_id INTEGER,
            description TEXT,
            created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 2. 文献主表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS literature_main (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_zh VARCHAR(255) NOT NULL,
            title_sanskrit VARCHAR(255),
            title_pali VARCHAR(255),
            title_english VARCHAR(255),
            author VARCHAR(255),
            compilation_period VARCHAR(100),
            original_language VARCHAR(50),
            translation_versions TEXT,  -- JSON格式存储
            category_id INTEGER,
            importance_level INTEGER CHECK(importance_level BETWEEN 1 AND 10),
            research_hotspot BOOLEAN DEFAULT 0,
            digital_status VARCHAR(50),
            file_path VARCHAR(500),
            summary_zh TEXT,
            summary_en TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES literature_categories(id)
        )
        ''')
        
        # 3. 关键概念表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS key_concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept_name VARCHAR(255) NOT NULL,
            concept_sanskrit VARCHAR(255),
            concept_pali VARCHAR(255),
            description_zh TEXT,
            description_en TEXT,
            related_texts TEXT,  -- JSON格式存储
            importance_score INTEGER CHECK(importance_score BETWEEN 1 AND 10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 4. 文献-概念关联表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS literature_concepts (
            literature_id INTEGER,
            concept_id INTEGER,
            relevance_level INTEGER CHECK(relevance_level BETWEEN 1 AND 5),
            chapter_section VARCHAR(100),
            PRIMARY KEY (literature_id, concept_id),
            FOREIGN KEY (literature_id) REFERENCES literature_main(id),
            FOREIGN KEY (concept_id) REFERENCES key_concepts(id)
        )
        ''')
        
        # 5. 研究价值评估表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS research_value (
            literature_id INTEGER PRIMARY KEY,
            assessed_by VARCHAR(100),
            academic_value INTEGER CHECK(academic_value BETWEEN 1 AND 10),
            research_potential INTEGER CHECK(research_potential BETWEEN 1 AND 10),
            accessibility INTEGER CHECK(accessibility BETWEEN 1 AND 10),
            notes TEXT,
            assessment_date DATE,
            FOREIGN KEY (literature_id) REFERENCES literature_main(id)
        )
        ''')
        
        # 6. 数字化状态表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS digitalization_status (
            literature_id INTEGER PRIMARY KEY,
            format_available TEXT,  -- JSON格式存储
            quality_rating INTEGER CHECK(quality_rating BETWEEN 1 AND 5),
            source_url VARCHAR(500),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (literature_id) REFERENCES literature_main(id)
        )
        ''')
        
        self.conn.commit()
        print("✅ 数据库表结构创建完成")
    
    def insert_category(self, category_data: Dict[str, Any]):
        """插入分类数据"""
        query = '''
        INSERT INTO literature_categories 
        (category_name, parent_id, description, created_by)
        VALUES (?, ?, ?, ?)
        '''
        self.cursor.execute(query, (
            category_data['category_name'],
            category_data.get('parent_id'),
            category_data.get('description'),
            category_data.get('created_by', 'mini')
        ))
        return self.cursor.lastrowid
    
    def insert_literature(self, literature_data: Dict[str, Any]):
        """插入文献数据"""
        # 处理JSON字段
        translation_versions = json.dumps(literature_data.get('translation_versions', {}), ensure_ascii=False)
        
        query = '''
        INSERT INTO literature_main 
        (title_zh, title_sanskrit, title_pali, title_english, 
         author, compilation_period, original_language, translation_versions,
         category_id, importance_level, research_hotspot, digital_status,
         file_path, summary_zh, summary_en)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        self.cursor.execute(query, (
            literature_data['title_zh'],
            literature_data.get('title_sanskrit'),
            literature_data.get('title_pali'),
            literature_data.get('title_english'),
            literature_data.get('author'),
            literature_data.get('compilation_period'),
            literature_data.get('original_language'),
            translation_versions,
            literature_data.get('category_id'),
            literature_data.get('importance_level', 5),
            1 if literature_data.get('research_hotspot') else 0,
            literature_data.get('digital_status', '未数字化'),
            literature_data.get('file_path'),
            literature_data.get('summary_zh'),
            literature_data.get('summary_en')
        ))
        
        return self.cursor.lastrowid
    
    def import_from_csv(self, csv_file_path: str):
        """从CSV文件导入数据"""
        print(f"🔄 正在从CSV文件导入数据: {csv_file_path}")
        
        with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            records_imported = 0
            
            for row in reader:
                try:
                    # 转换数据格式
                    literature_data = {
                        'title_zh': row.get('title_zh', ''),
                        'title_sanskrit': row.get('title_sanskrit'),
                        'title_pali': row.get('title_pali'),
                        'title_english': row.get('title_english'),
                        'author': row.get('author'),
                        'compilation_period': row.get('compilation_period'),
                        'original_language': row.get('original_language'),
                        'translation_versions': json.loads(row.get('translation_versions', '{}')),
                        'category_id': int(row['category_id']) if row.get('category_id') else None,
                        'importance_level': int(row.get('importance_level', 5)),
                        'research_hotspot': row.get('research_hotspot', '').lower() == 'true',
                        'digital_status': row.get('digital_status', '未数字化'),
                        'file_path': row.get('file_path'),
                        'summary_zh': row.get('summary_zh'),
                        'summary_en': row.get('summary_en')
                    }
                    
                    self.insert_literature(literature_data)
                    records_imported += 1
                    
                    if records_imported % 10 == 0:
                        print(f"  已导入 {records_imported} 条记录...")
                        
                except Exception as e:
                    print(f"⚠️ 导入记录时出错: {row.get('title_zh', '未知')} - {e}")
                    continue
            
            self.conn.commit()
            print(f"✅ CSV导入完成！共导入 {records_imported} 条记录")
    
    def import_from_json(self, json_file_path: str):
        """从JSON文件导入数据"""
        print(f"🔄 正在从JSON文件导入数据: {json_file_path}")
        
        with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            records_imported = 0
            
            if isinstance(data, list):
                for item in data:
                    try:
                        self.insert_literature(item)
                        records_imported += 1
                    except Exception as e:
                        print(f"⚠️ 导入记录时出错: {item.get('title_zh', '未知')} - {e}")
                        continue
            elif isinstance(data, dict):
                # 如果是包含分类的数据结构
                if 'categories' in data:
                    for category in data['categories']:
                        category_id = self.insert_category(category)
                        print(f"  添加分类: {category['category_name']} (ID: {category_id})")
                
                if 'literatures' in data:
                    for literature in data['literatures']:
                        try:
                            self.insert_literature(literature)
                            records_imported += 1
                        except Exception as e:
                            print(f"⚠️ 导入记录时出错: {literature.get('title_zh', '未知')} - {e}")
                            continue
            
            self.conn.commit()
            print(f"✅ JSON导入完成！共导入 {records_imported} 条记录")
    
    def export_to_csv(self, output_file: str = "literature_export.csv"):
        """导出数据到CSV文件"""
        print(f"🔄 正在导出数据到CSV: {output_file}")
        
        query = '''
        SELECT 
            title_zh, title_sanskrit, title_pali, title_english,
            author, compilation_period, original_language,
            translation_versions, category_id, importance_level,
            research_hotspot, digital_status, file_path,
            summary_zh, summary_en
        FROM literature_main
        '''
        
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)
            writer.writerows(rows)
        
        print(f"✅ 数据导出完成！共导出 {len(rows)} 条记录到 {output_file}")
    
    def generate_report(self):
        """生成数据报告"""
        print("\n📊 数据库统计报告")
        print("=" * 50)
        
        # 统计文献数量
        self.cursor.execute("SELECT COUNT(*) FROM literature_main")
        total_literatures = self.cursor.fetchone()[0]
        print(f"文献总数: {total_literatures}")
        
        # 按分类统计
        self.cursor.execute('''
        SELECT c.category_name, COUNT(l.id) as count
        FROM literature_main l
        JOIN literature_categories c ON l.category_id = c.id
        GROUP BY c.category_name
        ORDER BY count DESC
        ''')
        
        print("\n📁 按分类统计:")
        for category, count in self.cursor.fetchall():
            print(f"  {category}: {count} 篇")
        
        # 重要性分布
        self.cursor.execute('''
        SELECT importance_level, COUNT(*) as count
        FROM literature_main
        GROUP BY importance_level
        ORDER BY importance_level DESC
        ''')
        
        print("\n⭐ 重要性等级分布:")
        for level, count in self.cursor.fetchall():
            print(f"  等级 {level}: {count} 篇")
        
        # 研究热点统计
        self.cursor.execute("SELECT COUNT(*) FROM literature_main WHERE research_hotspot = 1")
        hotspot_count = self.cursor.fetchone()[0]
        print(f"\n🔥 研究热点文献: {hotspot_count} 篇 ({hotspot_count/total_literatures*100:.1f}%)")
        
        # 数字化状态
        self.cursor.execute('''
        SELECT digital_status, COUNT(*) as count
        FROM literature_main
        GROUP BY digital_status
        ''')
        
        print("\n💾 数字化状态:")
        for status, count in self.cursor.fetchall():
            print(f"  {status}: {count} 篇")
        
        print("=" * 50)

def main():
    """主函数"""
    print("=" * 60)
    print("📚 佛学文献数据导入工具 v1.0")
    print("作者: ds | 为mini设计的协作工具")
    print("=" * 60)
    
    # 创建导入器实例
    importer = LiteratureDataImporter()
    
    try:
        # 连接数据库
        importer.connect()
        
        # 设置数据库结构
        importer.setup_database()
        
        # 演示：添加示例分类
        print("\n🔄 正在添加示例分类...")
        categories = [
            {
                'category_name': '原始佛典',
                'description': '佛陀直接教导的经典',
                'created_by': 'mini'
            },
            {
                'category_name': '大乘经典',
                'description': '大乘佛教重要经典',
                'created_by': 'mini'
            }
        ]
        
        for category in categories:
            category_id = importer.insert_category(category)
            print(f"  添加分类: {category['category_name']} (ID: {category_id})")
        
        importer.conn.commit()
        
        # 演示：添加示例文献
        print("\n🔄 正在添加示例文献...")
        example_literature = {
            'title_zh': '《金刚般若波罗蜜经》',
            'title_sanskrit': 'Vajracchedikā Prajñāpāramitā Sūtra',
            'title_english': 'Diamond Sutra',
            'author': '佛陀',
            'compilation_period': '公元1世纪',
            'original_language': '梵文',
            'translation_versions': {
                '中文': ['鸠摩罗什译', '玄奘译'],
                '英文': ['BDK English Tripitaka']
            },
            'category_id': 2,  # 大乘经典
            'importance_level': 9,
            'research_hotspot': True,
            'digital_status': '已数字化',
            'file_path': '/texts/mahayana/diamond_sutra.pdf',
            'summary_zh': '般若经典的核心，阐述空性智慧',
            'summary_en': 'Core Prajñāpāramitā text expounding emptiness wisdom'
        }
        
        literature_id = importer.insert_literature(example_literature)
        print(f"  添加文献: {example_literature['title_zh']} (ID: {literature_id})")
        
        importer.conn.commit()
        
        # 生成报告
        importer.generate_report()
        
        # 导出示例数据
        importer.export_to_csv("示例导出.csv")
        
        print("\n🎯 使用说明:")
        print("1. 准备CSV文件，包含文献数据")
        print("2. 运行: python 文献数据导入工具.py --csv 你的文件.csv")
        print("3. 或准备JSON文件，运行: python 文献数据导入工具.py --json 你的文件.json")
        print("4. 查看报告: python 文献数据导入工具.py --report")
        
    except Exception as e:
        print(f"❌ 出错: {e}")
    finally:
        importer.disconnect()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='佛学文献数据导入工具')
    parser.add_argument('--csv', help='从CSV文件导入数据')
    parser.add_argument('--json', help='从JSON文件导入数据')
    parser.add_argument('--export', help='导出数据到CSV文件', default='literature_export.csv')
    parser.add_argument('--report', action='store_true', help='生成数据报告')
    parser.add_argument('--setup', action='store_true', help='仅设置数据库结构')
    
    args = parser.parse_args()
    
    if args.csv or args.json or args.report or args.setup:
        # 命令行模式
        importer = LiteratureDataImporter()
        importer.connect()
        
        if args.setup:
            importer.setup_database()
            print("✅ 数据库结构设置完成")
        
        if args.csv:
            importer.import_from_csv(args.csv)
        
        if args.json:
            importer.import_from_json(args.json)
        
        if args.report:
            importer.generate_report()
        
        if args.export and (args.csv or args.json):
            importer.export_to_csv(args.export)
        
        importer.disconnect()
    else:
        # 交互式演示模式
        main()