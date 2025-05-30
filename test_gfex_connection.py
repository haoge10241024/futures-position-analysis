#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广期所数据获取测试脚本
用于诊断广期所数据获取问题
作者：7haoge
邮箱：953534947@qq.com
"""

import akshare as ak
import time
import signal
import sys
from datetime import datetime, timedelta

def timeout_handler(signum, frame):
    raise TimeoutError("数据获取超时")

def test_gfex_connection(trade_date: str = None):
    """测试广期所数据连接"""
    if trade_date is None:
        # 使用昨天的日期
        yesterday = datetime.now() - timedelta(days=1)
        trade_date = yesterday.strftime("%Y%m%d")
    
    print(f"🔍 测试广期所数据获取 - 日期: {trade_date}")
    print("=" * 50)
    
    # 测试1: 基本连接测试
    print("\n📡 测试1: 基本网络连接")
    try:
        import requests
        response = requests.get("https://www.gfex.com.cn", timeout=10)
        if response.status_code == 200:
            print("✅ 广期所官网连接正常")
        else:
            print(f"⚠️ 广期所官网响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 广期所官网连接失败: {str(e)}")
    
    # 测试2: akshare版本检查
    print("\n📦 测试2: akshare版本检查")
    try:
        print(f"akshare版本: {ak.__version__}")
        if hasattr(ak, 'futures_gfex_position_rank'):
            print("✅ futures_gfex_position_rank 函数存在")
        else:
            print("❌ futures_gfex_position_rank 函数不存在")
    except Exception as e:
        print(f"❌ akshare版本检查失败: {str(e)}")
    
    # 测试3: 无超时数据获取测试
    print("\n⏱️ 测试3: 无超时数据获取测试")
    try:
        start_time = time.time()
        print("正在获取广期所数据（无超时限制）...")
        data = ak.futures_gfex_position_rank(date=trade_date)
        elapsed_time = time.time() - start_time
        
        if data:
            print(f"✅ 数据获取成功！耗时: {elapsed_time:.2f} 秒")
            print(f"📊 获取到 {len(data)} 个品种的数据")
            print("品种列表:", list(data.keys())[:5], "..." if len(data) > 5 else "")
        else:
            print(f"⚠️ 数据为空，耗时: {elapsed_time:.2f} 秒")
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ 数据获取失败，耗时: {elapsed_time:.2f} 秒")
        print(f"错误信息: {str(e)}")
    
    # 测试4: 带超时的数据获取测试
    print("\n⏰ 测试4: 带超时的数据获取测试（15秒）")
    
    # 设置超时信号（仅在非Windows系统）
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(15)
    
    try:
        start_time = time.time()
        print("正在获取广期所数据（15秒超时）...")
        data = ak.futures_gfex_position_rank(date=trade_date)
        elapsed_time = time.time() - start_time
        
        # 取消超时信号
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        
        if data:
            print(f"✅ 数据获取成功！耗时: {elapsed_time:.2f} 秒")
            print(f"📊 获取到 {len(data)} 个品种的数据")
        else:
            print(f"⚠️ 数据为空，耗时: {elapsed_time:.2f} 秒")
            
    except TimeoutError:
        print("⏰ 数据获取超时（15秒）")
        print("💡 建议: 广期所数据获取较慢，可以跳过该交易所")
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ 数据获取失败，耗时: {elapsed_time:.2f} 秒")
        print(f"错误信息: {str(e)}")
    finally:
        # 确保清理超时信号
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
    
    # 测试5: 重试机制测试
    print("\n🔄 测试5: 重试机制测试")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"尝试 {attempt + 1}/{max_retries}...")
            start_time = time.time()
            
            # 设置较短超时
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(10)
            
            data = ak.futures_gfex_position_rank(date=trade_date)
            elapsed_time = time.time() - start_time
            
            # 取消超时信号
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            
            if data:
                print(f"✅ 第 {attempt + 1} 次尝试成功！耗时: {elapsed_time:.2f} 秒")
                break
            else:
                print(f"⚠️ 第 {attempt + 1} 次尝试数据为空")
                
        except (TimeoutError, Exception) as e:
            elapsed_time = time.time() - start_time
            print(f"❌ 第 {attempt + 1} 次尝试失败，耗时: {elapsed_time:.2f} 秒")
            print(f"错误: {str(e)}")
            
            if attempt < max_retries - 1:
                print("等待2秒后重试...")
                time.sleep(2)
        finally:
            # 确保清理超时信号
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
    
    print("\n" + "=" * 50)
    print("🎯 测试总结:")
    print("1. 如果所有测试都失败，说明网络连接有问题")
    print("2. 如果无超时测试成功但带超时测试失败，说明数据获取较慢")
    print("3. 如果重试机制有成功的，说明网络不稳定")
    print("4. 建议在系统中跳过广期所或增加超时时间")
    print("\n💡 解决方案:")
    print("- 在网络良好的环境下使用")
    print("- 增加广期所数据获取的超时时间")
    print("- 或者在分析中跳过广期所数据")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_date = sys.argv[1]
    else:
        test_date = None
    
    test_gfex_connection(test_date) 