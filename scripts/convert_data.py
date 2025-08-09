#!/usr/bin/env python3
"""
数据转换工具：CSV/Excel 转 JSONL
支持批量转换和直接导入到数据库
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import pandas as pd
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.data_manager import init_db, insert_faqs, rebuild_fts
from app.utils.logger import logger as app_logger


class DataConverter:
    """数据转换器"""
    
    def __init__(self):
        self.required_columns = ['question', 'answer']
        self.optional_columns = ['language', 'tags', 'source']
        self.all_columns = self.required_columns + self.optional_columns
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """验证数据格式"""
        errors = []
        
        # 检查必需列
        missing_cols = [col for col in self.required_columns if col not in df.columns]
        if missing_cols:
            errors.append(f"缺少必需列: {missing_cols}")
            return df, errors
        
        # 检查数据完整性
        original_count = len(df)
        
        # 移除question或answer为空的行
        df = df.dropna(subset=['question', 'answer'])
        df = df[df['question'].str.strip() != '']
        df = df[df['answer'].str.strip() != '']
        
        dropped_count = original_count - len(df)
        if dropped_count > 0:
            errors.append(f"移除了 {dropped_count} 行空数据")
        
        # 处理可选列
        for col in self.optional_columns:
            if col not in df.columns:
                if col == 'language':
                    df[col] = 'auto'
                elif col == 'tags':
                    df[col] = ''
                elif col == 'source':
                    df[col] = 'imported'
        
        # 处理tags列（转换为逗号分隔的字符串）
        if 'tags' in df.columns:
            df['tags'] = df['tags'].fillna('').astype(str)
            # 如果tags包含列表格式，转换为逗号分隔
            df['tags'] = df['tags'].apply(self._process_tags)
        
        return df, errors
    
    def _process_tags(self, tags_value: Any) -> str:
        """处理tags字段"""
        if pd.isna(tags_value) or tags_value == '':
            return ''
        
        if isinstance(tags_value, str):
            # 如果是字符串，直接返回
            return tags_value.strip()
        elif isinstance(tags_value, (list, tuple)):
            # 如果是列表，转换为逗号分隔
            return ','.join(str(tag).strip() for tag in tags_value if str(tag).strip())
        else:
            return str(tags_value).strip()
    
    def read_file(self, file_path: str) -> pd.DataFrame:
        """读取文件"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            if file_path.suffix.lower() == '.csv':
                # 尝试不同编码读取CSV
                for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        logger.info(f"成功读取CSV文件 (编码: {encoding}): {len(df)} 行")
                        return df
                    except UnicodeDecodeError:
                        continue
                raise ValueError("无法读取CSV文件，请检查文件编码")
            
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                logger.info(f"成功读取Excel文件: {len(df)} 行")
                return df
            
            else:
                raise ValueError(f"不支持的文件格式: {file_path.suffix}")
        
        except Exception as e:
            raise ValueError(f"读取文件失败: {e}")
    
    def convert_to_jsonl(self, df: pd.DataFrame, output_path: str) -> int:
        """转换为JSONL格式"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        count = 0
        with open(output_path, 'w', encoding='utf-8') as f:
            for _, row in df.iterrows():
                item = {
                    'question': str(row['question']).strip(),
                    'answer': str(row['answer']).strip(),
                    'language': str(row.get('language', 'auto')).strip(),
                    'source': str(row.get('source', 'imported')).strip()
                }
                
                # 处理tags
                tags_str = str(row.get('tags', '')).strip()
                if tags_str:
                    # 分割tags并清理（支持逗号和分号分隔）
                    tags = []
                    for separator in [',', ';']:
                        if separator in tags_str:
                            tags = [tag.strip() for tag in tags_str.split(separator) if tag.strip()]
                            break
                    if not tags:  # 如果没有分隔符，整个字符串作为一个tag
                        tags = [tags_str]
                    item['tags'] = tags
                else:
                    item['tags'] = []
                
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
                count += 1
        
        logger.info(f"转换完成: {count} 条记录写入 {output_path}")
        return count
    
    def import_to_database(self, df: pd.DataFrame, rebuild_index: bool = True) -> int:
        """直接导入到数据库"""
        init_db()
        
        rows = []
        for _, row in df.iterrows():
            tags_str = str(row.get('tags', '')).strip()
            if tags_str:
                # 处理tags为逗号分隔的字符串
                tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                tags_final = ','.join(tags) if tags else None
            else:
                tags_final = None
            
            rows.append((
                str(row['question']).strip(),
                str(row['answer']).strip(),
                str(row.get('language', 'auto')).strip(),
                tags_final,
                str(row.get('source', 'imported')).strip()
            ))
        
        count = insert_faqs(rows)
        
        if rebuild_index:
            rebuild_fts()
            logger.info("已重建全文索引")
        
        logger.info(f"成功导入 {count} 条记录到数据库")
        return count


def main():
    parser = argparse.ArgumentParser(description='数据转换工具：CSV/Excel 转 JSONL 或直接导入数据库')
    parser.add_argument('input_file', help='输入文件路径 (CSV/Excel)')
    parser.add_argument('-o', '--output', help='输出JSONL文件路径 (不指定则直接导入数据库)')
    parser.add_argument('--no-rebuild', action='store_true', help='导入数据库时不重建索引')
    parser.add_argument('--preview', action='store_true', help='预览模式：只显示前5行数据，不执行转换')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 配置日志
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    converter = DataConverter()
    
    try:
        # 读取文件
        logger.info(f"读取文件: {args.input_file}")
        df = converter.read_file(args.input_file)
        
        # 验证数据
        logger.info("验证数据格式...")
        df_clean, errors = converter.validate_data(df)
        
        if errors:
            logger.warning("数据验证警告:")
            for error in errors:
                logger.warning(f"  - {error}")
        
        if len(df_clean) == 0:
            logger.error("没有有效数据可处理")
            return 1
        
        logger.info(f"有效数据: {len(df_clean)} 行")
        
        # 预览模式
        if args.preview:
            logger.info("预览前5行数据:")
            print("\n" + "="*80)
            for i, (_, row) in enumerate(df_clean.head().iterrows()):
                print(f"第 {i+1} 行:")
                print(f"  问题: {row['question']}")
                print(f"  答案: {row['answer']}")
                print(f"  语言: {row.get('language', 'auto')}")
                print(f"  标签: {row.get('tags', '')}")
                print(f"  来源: {row.get('source', 'imported')}")
                print("-" * 40)
            print("="*80)
            return 0
        
        # 执行转换或导入
        if args.output:
            # 转换为JSONL
            count = converter.convert_to_jsonl(df_clean, args.output)
            logger.success(f"转换完成: {count} 条记录")
        else:
            # 直接导入数据库
            count = converter.import_to_database(df_clean, not args.no_rebuild)
            logger.success(f"导入完成: {count} 条记录")
        
        return 0
    
    except Exception as e:
        logger.error(f"处理失败: {e}")
        if args.verbose:
            logger.exception("详细错误信息:")
        return 1


if __name__ == '__main__':
    sys.exit(main())
