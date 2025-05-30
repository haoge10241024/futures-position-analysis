#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端部署配置文件
专门优化Streamlit Cloud部署参数
作者：7haoge
邮箱：953534947@qq.com
"""

# 云端数据获取配置
CLOUD_CONFIG = {
    # 超时设置（秒）
    "timeouts": {
        "大商所": 30,
        "中金所": 30,
        "郑商所": 30,
        "上期所": 30,
        "广期所": 45,  # 广期所给更多时间
        "行情数据": 30
    },
    
    # 重试配置
    "retries": {
        "大商所": 2,
        "中金所": 2,
        "郑商所": 2,
        "上期所": 2,
        "广期所": 3,  # 广期所多重试一次
        "行情数据": 2
    },
    
    # 并发配置
    "concurrency": {
        "max_workers": 2,  # 云端限制并发数
        "chunk_size": 2,   # 分批处理
        "delay_between_batches": 1  # 批次间延迟（秒）
    },
    
    # 缓存配置
    "cache": {
        "data_ttl": 3600,      # 数据缓存1小时
        "analysis_ttl": 1800,  # 分析结果缓存30分钟
        "max_cache_files": 50, # 最大缓存文件数
        "cleanup_days": 3      # 3天后清理缓存
    },
    
    # 错误处理配置
    "error_handling": {
        "skip_on_timeout": True,     # 超时时跳过
        "continue_on_error": True,   # 出错时继续
        "min_success_rate": 0.6,     # 最小成功率60%
        "show_detailed_errors": False # 不显示详细错误（避免用户困惑）
    },
    
    # 用户体验配置
    "ui": {
        "show_progress": True,       # 显示进度
        "show_timing": True,         # 显示耗时
        "show_cache_status": True,   # 显示缓存状态
        "auto_retry": True,          # 自动重试
        "friendly_messages": True    # 友好的消息提示
    }
}

# 云端环境检测
def is_cloud_environment():
    """检测是否在云端环境运行"""
    import os
    # Streamlit Cloud环境变量
    return (
        os.getenv('STREAMLIT_SHARING_MODE') is not None or
        os.getenv('STREAMLIT_CLOUD') is not None or
        'streamlit.io' in os.getenv('HOSTNAME', '') or
        'share.streamlit.io' in os.getenv('SERVER_NAME', '')
    )

# 获取适合云端的配置
def get_cloud_optimized_config():
    """获取云端优化配置"""
    if is_cloud_environment():
        return CLOUD_CONFIG
    else:
        # 本地环境使用更宽松的配置
        local_config = CLOUD_CONFIG.copy()
        local_config["timeouts"]["广期所"] = 60  # 本地给广期所更多时间
        local_config["concurrency"]["max_workers"] = 3  # 本地可以更多并发
        return local_config

# 应用云端优化
def apply_cloud_optimizations():
    """应用云端优化设置"""
    config = get_cloud_optimized_config()
    
    if is_cloud_environment():
        print("🌐 检测到云端环境，应用云端优化配置")
        print(f"- 广期所超时: {config['timeouts']['广期所']}秒")
        print(f"- 最大并发数: {config['concurrency']['max_workers']}")
        print(f"- 重试次数: {config['retries']['广期所']}")
    else:
        print("💻 本地环境，使用标准配置")
    
    return config 