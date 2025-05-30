#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期货持仓分析系统 - 性能优化模块
专门用于提升云端部署性能
作者：7haoge
邮箱：953534947@qq.com
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import pickle
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import concurrent.futures
from functools import wraps
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.ensure_cache_directory()
        self.session = self.create_optimized_session()
        
    def ensure_cache_directory(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def create_optimized_session(self):
        """创建优化的HTTP会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置超时
        session.timeout = 30
        
        return session
    
    def get_cache_key(self, func_name: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{func_name}_{str(args)}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cache_path(self, cache_key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    def is_cache_valid(self, cache_path: str, max_age_hours: int = 24) -> bool:
        """检查缓存是否有效"""
        if not os.path.exists(cache_path):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        return datetime.now() - file_time < timedelta(hours=max_age_hours)
    
    def save_to_cache(self, cache_key: str, data: Any):
        """保存数据到缓存"""
        try:
            cache_path = self.get_cache_path(cache_key)
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            st.warning(f"缓存保存失败: {str(e)}")
    
    def load_from_cache(self, cache_key: str) -> Optional[Any]:
        """从缓存加载数据"""
        try:
            cache_path = self.get_cache_path(cache_key)
            if self.is_cache_valid(cache_path):
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            st.warning(f"缓存加载失败: {str(e)}")
        return None
    
    def clear_old_cache(self, max_age_days: int = 7):
        """清理旧缓存"""
        try:
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    file_path = os.path.join(self.cache_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_time:
                        os.remove(file_path)
        except Exception as e:
            st.warning(f"缓存清理失败: {str(e)}")

# 全局优化器实例
optimizer = PerformanceOptimizer()

def smart_cache(max_age_hours: int = 24):
    """智能缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = optimizer.get_cache_key(func.__name__, *args, **kwargs)
            
            # 尝试从缓存加载
            cached_data = optimizer.load_from_cache(cache_key)
            if cached_data is not None:
                st.info(f"✅ 使用缓存数据 - {func.__name__}")
                return cached_data
            
            # 执行函数
            st.info(f"🔄 正在获取新数据 - {func.__name__}")
            result = func(*args, **kwargs)
            
            # 保存到缓存
            if result is not None:
                optimizer.save_to_cache(cache_key, result)
            
            return result
        return wrapper
    return decorator

@st.cache_data(ttl=3600)  # Streamlit缓存1小时
def cached_data_fetch(func_name: str, date: str, exchange: str = None):
    """缓存的数据获取函数 - 增强版本，包含超时控制"""
    import akshare as ak
    import signal
    import time
    
    def timeout_handler(signum, frame):
        raise TimeoutError("数据获取超时")
    
    try:
        # 为广期所设置更长的超时时间
        if func_name == "futures_gfex_position_rank":
            timeout_seconds = 30  # 广期所30秒超时（从15秒增加）
        else:
            timeout_seconds = 30  # 其他交易所30秒超时
        
        # 设置超时信号（仅在非Windows系统）
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
        
        start_time = time.time()
        
        if func_name == "futures_dce_position_rank":
            result = ak.futures_dce_position_rank(date=date)
        elif func_name == "get_cffex_rank_table":
            result = ak.get_cffex_rank_table(date=date)
        elif func_name == "get_czce_rank_table":
            result = ak.get_czce_rank_table(date=date)
        elif func_name == "get_shfe_rank_table":
            result = ak.get_shfe_rank_table(date=date)
        elif func_name == "futures_gfex_position_rank":
            # 广期所特殊处理 - 添加重试机制
            max_retries = 3  # 增加重试次数
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        st.info(f"🔄 广期所数据获取重试 {attempt}/{max_retries-1}")
                    result = ak.futures_gfex_position_rank(date=date)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        st.warning(f"广期所数据获取失败（已重试{max_retries}次），跳过该交易所: {str(e)}")
                        return None
                    time.sleep(3)  # 重试前等待3秒（增加等待时间）
        elif func_name == "get_futures_daily" and exchange:
            result = ak.get_futures_daily(start_date=date, end_date=date, market=exchange)
        else:
            return None
        
        # 取消超时信号
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        
        elapsed_time = time.time() - start_time
        if elapsed_time > 8:  # 如果超过8秒，显示提示
            st.info(f"⏱️ {func_name} 数据获取耗时 {elapsed_time:.1f} 秒")
        
        return result
        
    except TimeoutError:
        st.warning(f"⏰ {func_name} 数据获取超时，跳过该交易所")
        return None
    except Exception as e:
        st.warning(f"❌ {func_name} 数据获取失败: {str(e)}")
        return None
    finally:
        # 确保清理超时信号
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)

class FastDataManager:
    """快速数据管理器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.optimizer = optimizer
        
        # 交易所配置 - 按优先级排序
        self.exchange_config = {
            "大商所": {
                "func_name": "futures_dce_position_rank",
                "filename": "大商所持仓.xlsx",
                "priority": 1,
                "timeout": 30
            },
            "中金所": {
                "func_name": "get_cffex_rank_table", 
                "filename": "中金所持仓.xlsx",
                "priority": 2,
                "timeout": 30
            },
            "郑商所": {
                "func_name": "get_czce_rank_table",
                "filename": "郑商所持仓.xlsx", 
                "priority": 3,
                "timeout": 30
            },
            "上期所": {
                "func_name": "get_shfe_rank_table",
                "filename": "上期所持仓.xlsx",
                "priority": 4,
                "timeout": 30
            },
            "广期所": {
                "func_name": "futures_gfex_position_rank",
                "filename": "广期所持仓.xlsx",
                "priority": 5,
                "timeout": 30
            }
        }
    
    def fetch_position_data_fast(self, trade_date: str, progress_callback=None) -> bool:
        """快速获取持仓数据 - 使用并发和缓存，优化广期所处理"""
        success_count = 0
        total_exchanges = len(self.exchange_config)
        failed_exchanges = []
        
        # 重新排序，将广期所放到最后处理
        sorted_exchanges = sorted(
            self.exchange_config.items(), 
            key=lambda x: x[1]['priority']
        )
        
        # 使用线程池并发获取数据，但限制并发数避免网络拥堵
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_exchange = {}
            
            for exchange_name, config in sorted_exchanges:
                future = executor.submit(
                    self._fetch_single_exchange_data_with_timeout,
                    exchange_name, config, trade_date
                )
                future_to_exchange[future] = exchange_name
            
            # 处理完成的任务
            for i, future in enumerate(concurrent.futures.as_completed(future_to_exchange)):
                exchange_name = future_to_exchange[future]
                
                if progress_callback:
                    progress = (i + 1) / total_exchanges * 0.6
                    progress_callback(f"已完成 {exchange_name} 数据获取", progress)
                
                try:
                    success = future.result(timeout=60)  # 60秒总超时（增加超时时间）
                    if success:
                        success_count += 1
                        st.success(f"✅ {exchange_name} 数据获取成功")
                    else:
                        failed_exchanges.append(exchange_name)
                        st.warning(f"⚠️ {exchange_name} 数据获取失败，但不影响其他交易所")
                except Exception as e:
                    failed_exchanges.append(exchange_name)
                    st.warning(f"⚠️ {exchange_name} 数据获取异常: {str(e)}")
                    continue
        
        if progress_callback:
            progress_callback("持仓数据获取完成", 0.6)
        
        # 显示获取结果摘要
        if success_count > 0:
            st.info(f"📊 成功获取 {success_count}/{total_exchanges} 个交易所数据")
            if failed_exchanges:
                st.info(f"⚠️ 未获取到数据的交易所: {', '.join(failed_exchanges)}")
        
        return success_count > 0
    
    def _fetch_single_exchange_data_with_timeout(self, exchange_name: str, config: dict, trade_date: str) -> bool:
        """获取单个交易所数据 - 增强版本，包含特殊处理"""
        try:
            # 广期所特殊处理
            if exchange_name == "广期所":
                st.info(f"🔄 正在尝试获取{exchange_name}数据（可能较慢）...")
            
            # 使用缓存的数据获取函数
            data_dict = cached_data_fetch(config["func_name"], trade_date)
            
            if data_dict:
                # 保存到Excel
                save_path = os.path.join(self.data_dir, config['filename'])
                with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                    for sheet_name, df in data_dict.items():
                        # 清理sheet名称
                        clean_name = sheet_name[:31].replace("/", "-").replace("*", "")
                        df.to_excel(writer, sheet_name=clean_name, index=False)
                
                return True
            else:
                # 如果是广期所失败，给出特殊提示
                if exchange_name == "广期所":
                    st.info("ℹ️ 广期所数据暂时无法获取，这是常见情况，不影响其他分析")
                return False
            
        except Exception as e:
            if exchange_name == "广期所":
                st.info(f"ℹ️ 广期所数据获取遇到问题: {str(e)}，继续处理其他交易所")
            else:
                st.warning(f"获取{exchange_name}数据失败: {str(e)}")
            return False
    
    @smart_cache(max_age_hours=6)
    def fetch_price_data_fast(self, trade_date: str, progress_callback=None) -> pd.DataFrame:
        """快速获取期货行情数据"""
        price_exchanges = [
            {"market": "DCE", "name": "大商所"},
            {"market": "CFFEX", "name": "中金所"}, 
            {"market": "CZCE", "name": "郑商所"},
            {"market": "SHFE", "name": "上期所"},
        ]
        
        all_data = []
        
        # 并发获取行情数据
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_exchange = {}
            
            for exchange in price_exchanges:
                future = executor.submit(
                    cached_data_fetch,
                    "get_futures_daily",
                    trade_date,
                    exchange["market"]
                )
                future_to_exchange[future] = exchange
            
            for i, future in enumerate(concurrent.futures.as_completed(future_to_exchange)):
                exchange = future_to_exchange[future]
                
                if progress_callback:
                    progress = 0.6 + (i / len(price_exchanges)) * 0.2
                    progress_callback(f"已完成 {exchange['name']} 行情数据", progress)
                
                try:
                    df = future.result(timeout=30)
                    if df is not None and not df.empty:
                        df['exchange'] = exchange["name"]
                        all_data.append(df)
                except Exception as e:
                    st.warning(f"获取{exchange['name']}行情数据失败: {str(e)}")
                    continue
        
        if progress_callback:
            progress_callback("行情数据获取完成", 0.8)
        
        return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def optimize_streamlit_performance():
    """优化Streamlit性能"""
    # 清理旧缓存
    optimizer.clear_old_cache()
    
    # 设置Streamlit配置
    if 'performance_optimized' not in st.session_state:
        st.session_state.performance_optimized = True
        
        # 显示性能提示
        st.info("""
        🚀 **性能优化已启用**
        - ✅ 智能缓存系统
        - ✅ 并发数据获取  
        - ✅ 网络连接优化
        - ✅ 自动缓存清理
        
        首次运行可能较慢，后续会显著加速！
        """)

def show_performance_metrics():
    """显示性能指标"""
    cache_files = [f for f in os.listdir(optimizer.cache_dir) if f.endswith('.pkl')]
    cache_size = len(cache_files)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("缓存文件数", cache_size)
    
    with col2:
        if cache_size > 0:
            latest_cache = max(
                [os.path.join(optimizer.cache_dir, f) for f in cache_files],
                key=os.path.getmtime
            )
            cache_time = datetime.fromtimestamp(os.path.getmtime(latest_cache))
            st.metric("最新缓存", cache_time.strftime("%H:%M"))
        else:
            st.metric("最新缓存", "无")
    
    with col3:
        if st.button("🗑️ 清理缓存"):
            optimizer.clear_old_cache(max_age_days=0)  # 清理所有缓存
            st.success("缓存已清理")
            st.rerun() 
