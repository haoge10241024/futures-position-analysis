#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期货持仓分析系统 - 云端数据获取模块
专门解决Streamlit Cloud环境下的数据获取问题
作者：7haoge
邮箱：953534947@qq.com
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

class CloudDataFetcher:
    """云端数据获取器 - 专门处理云端环境的数据获取问题"""
    
    def __init__(self):
        self.session = self.create_session()
        self.max_retries = 3
        self.timeout = 30
        self.delay_between_requests = 2  # 请求间隔
        
    def create_session(self):
        """创建优化的请求会话"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        return session
    
    def safe_akshare_call(self, func, *args, **kwargs):
        """安全的akshare调用，包含重试机制"""
        for attempt in range(self.max_retries):
            try:
                # 添加延迟避免请求过快
                if attempt > 0:
                    time.sleep(self.delay_between_requests * attempt)
                
                result = func(*args, **kwargs)
                if result is not None:
                    return result
                    
            except Exception as e:
                error_msg = str(e)
                if attempt == self.max_retries - 1:
                    st.warning(f"数据获取失败 (尝试 {attempt + 1}/{self.max_retries}): {error_msg}")
                else:
                    st.info(f"重试中... (尝试 {attempt + 1}/{self.max_retries})")
                
                # 特定错误的处理
                if "timeout" in error_msg.lower():
                    time.sleep(5)  # 超时错误等待更长时间
                elif "rate limit" in error_msg.lower():
                    time.sleep(10)  # 频率限制等待更长时间
                    
        return None
    
    def fetch_position_data_with_fallback(self, trade_date: str, progress_callback=None) -> bool:
        """获取持仓数据，包含备用方案"""
        
        # 尝试导入akshare
        try:
            import akshare as ak
        except ImportError:
            st.error("akshare未安装，请联系管理员")
            return False
        
        success_count = 0
        total_exchanges = 5
        
        # 交易所配置 - 按成功率排序
        exchanges = [
            {
                "name": "大商所",
                "func": ak.futures_dce_position_rank,
                "filename": "大商所持仓.xlsx",
                "args": {"date": trade_date}
            },
            {
                "name": "中金所", 
                "func": ak.get_cffex_rank_table,
                "filename": "中金所持仓.xlsx",
                "args": {"date": trade_date}
            },
            {
                "name": "郑商所",
                "func": ak.get_czce_rank_table,
                "filename": "郑商所持仓.xlsx", 
                "args": {"date": trade_date}
            },
            {
                "name": "上期所",
                "func": ak.get_shfe_rank_table,
                "filename": "上期所持仓.xlsx",
                "args": {"date": trade_date}
            },
            {
                "name": "广期所",
                "func": ak.futures_gfex_position_rank,
                "filename": "广期所持仓.xlsx",
                "args": {"date": trade_date}
            }
        ]
        
        # 确保数据目录存在
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        for i, exchange in enumerate(exchanges):
            if progress_callback:
                progress = i / total_exchanges * 0.6
                progress_callback(f"正在获取 {exchange['name']} 数据...", progress)
            
            try:
                st.info(f"🔄 正在获取 {exchange['name']} 数据...")
                
                # 使用安全调用
                data_dict = self.safe_akshare_call(exchange['func'], **exchange['args'])
                
                if data_dict:
                    # 保存数据
                    save_path = os.path.join(data_dir, exchange['filename'])
                    with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                        for sheet_name, df in data_dict.items():
                            # 清理sheet名称
                            clean_name = sheet_name[:31].replace("/", "-").replace("*", "")
                            df.to_excel(writer, sheet_name=clean_name, index=False)
                    
                    st.success(f"✅ {exchange['name']} 数据获取成功")
                    success_count += 1
                else:
                    st.warning(f"⚠️ {exchange['name']} 数据获取失败，但不影响其他交易所")
                    
            except Exception as e:
                st.warning(f"⚠️ {exchange['name']} 数据获取失败: {str(e)}")
                continue
            
            # 添加请求间隔
            time.sleep(self.delay_between_requests)
        
        if progress_callback:
            progress_callback("持仓数据获取完成", 0.6)
        
        return success_count > 0
    
    def fetch_price_data_with_fallback(self, trade_date: str, progress_callback=None) -> pd.DataFrame:
        """获取期货行情数据，包含备用方案"""
        
        try:
            import akshare as ak
        except ImportError:
            st.error("akshare未安装，请联系管理员")
            return pd.DataFrame()
        
        price_exchanges = [
            {"market": "DCE", "name": "大商所"},
            {"market": "CFFEX", "name": "中金所"},
            {"market": "CZCE", "name": "郑商所"},
            {"market": "SHFE", "name": "上期所"},
        ]
        
        all_data = []
        
        for i, exchange in enumerate(price_exchanges):
            if progress_callback:
                progress = 0.6 + (i / len(price_exchanges)) * 0.2
                progress_callback(f"正在获取 {exchange['name']} 行情数据...", progress)
            
            try:
                st.info(f"🔄 正在获取 {exchange['name']} 行情数据...")
                
                # 使用安全调用
                df = self.safe_akshare_call(
                    ak.get_futures_daily,
                    start_date=trade_date,
                    end_date=trade_date,
                    market=exchange["market"]
                )
                
                if df is not None and not df.empty:
                    df['exchange'] = exchange["name"]
                    all_data.append(df)
                    st.success(f"✅ {exchange['name']} 行情数据获取成功")
                else:
                    st.warning(f"⚠️ {exchange['name']} 行情数据为空")
                    
            except Exception as e:
                st.warning(f"⚠️ {exchange['name']} 行情数据获取失败: {str(e)}")
                continue
            
            # 添加请求间隔
            time.sleep(self.delay_between_requests)
        
        if progress_callback:
            progress_callback("行情数据获取完成", 0.8)
        
        return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    
    def create_demo_data(self, trade_date: str) -> bool:
        """创建演示数据（当所有数据源都失败时）"""
        st.warning("⚠️ 所有数据源都无法访问，正在创建演示数据...")
        
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        # 创建演示持仓数据
        demo_contracts = ['螺纹钢2501', '铁矿石2501', '豆粕2501', '玉米2501', '白糖2501']
        
        for exchange_name in ['大商所', '中金所', '郑商所', '上期所', '广期所']:
            filename = f"{exchange_name}持仓.xlsx"
            save_path = os.path.join(data_dir, filename)
            
            # 创建演示数据
            demo_data = {}
            for contract in demo_contracts:
                # 生成随机但合理的持仓数据
                np.random.seed(hash(contract + trade_date) % 2**32)
                
                data = []
                for i in range(20):  # 前20名
                    data.append({
                        'long_party_name': f'期货公司{i+1}',
                        'long_open_interest': np.random.randint(1000, 50000),
                        'long_open_interest_chg': np.random.randint(-5000, 5000),
                        'short_party_name': f'期货公司{i+1}',
                        'short_open_interest': np.random.randint(1000, 50000),
                        'short_open_interest_chg': np.random.randint(-5000, 5000),
                    })
                
                demo_data[contract] = pd.DataFrame(data)
            
            # 保存演示数据
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                for sheet_name, df in demo_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        st.info("✅ 演示数据创建完成，您可以体验系统功能")
        return True
    
    def diagnose_network_issues(self):
        """诊断网络问题"""
        st.subheader("🔍 网络诊断")
        
        # 测试基本网络连接
        test_urls = [
            ("百度", "https://www.baidu.com"),
            ("新浪", "https://www.sina.com.cn"),
            ("akshare官网", "https://akshare.akfamily.xyz")
        ]
        
        for name, url in test_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    st.success(f"✅ {name} 连接正常")
                else:
                    st.warning(f"⚠️ {name} 连接异常 (状态码: {response.status_code})")
            except Exception as e:
                st.error(f"❌ {name} 连接失败: {str(e)}")
        
        # 测试akshare导入
        try:
            import akshare as ak
            st.success(f"✅ akshare 导入成功 (版本: {getattr(ak, '__version__', '未知')})")
        except ImportError:
            st.error("❌ akshare 导入失败")
        
        # 提供解决建议
        st.markdown("""
        ### 💡 解决建议
        
        如果数据获取失败，可能的原因和解决方案：
        
        1. **网络限制**: Streamlit Cloud可能限制某些外部API访问
           - 解决方案: 使用演示数据体验功能
        
        2. **API频率限制**: akshare的数据源可能有访问频率限制
           - 解决方案: 等待几分钟后重试
        
        3. **数据源维护**: 交易所数据源可能在维护
           - 解决方案: 选择其他交易日期
        
        4. **云端环境限制**: 某些云端环境对外部请求有限制
           - 解决方案: 本地运行或使用演示模式
        """)

# 全局实例
cloud_fetcher = CloudDataFetcher() 