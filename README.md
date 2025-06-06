# 期货持仓分析系统 v2.0

**作者：7haoge**  
**邮箱：953534947@qq.com**

## 📊 项目简介

期货持仓分析系统是一个基于Python和Streamlit的Web应用，专门用于分析期货市场的持仓数据。系统整合了多种分析策略，帮助投资者识别市场趋势和投资机会。

### ✨ 主要特性

- **多策略分析**: 集成多空力量变化、蜘蛛网、家人席位反向操作等策略
- **实时数据获取**: 自动从各大期货交易所获取最新持仓数据
- **智能信号识别**: 自动识别看多/看空信号并计算信号强度
- **信号共振分析**: 识别多策略共同看好的品种
- **期限结构分析**: 严格按照近月到远月价格关系分析同品种不同月份合约
- **可配置家人席位**: 用户可自定义散户席位配置
- **可视化展示**: 丰富的图表和数据可视化
- **详细持仓信息**: 支持查看每个信号的详细持仓数据
- **报告导出**: 支持Excel和文本格式的分析报告导出

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 稳定的网络连接
- 8GB+ 内存推荐

### 安装步骤

1. **克隆或下载项目**
   ```bash
   # 如果是从git克隆
   git clone <repository-url>
   cd 新程序
   
   # 或者直接进入新程序目录
   cd 新程序
   ```

2. **安装依赖包**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行系统测试**
   ```bash
   python test_system.py
   ```

4. **启动应用**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **打开浏览器**
   - 访问显示的URL（通常是 http://localhost:8501）
   - 开始使用系统

## 📋 系统架构

### 核心模块

```
新程序/
├── streamlit_app.py      # Streamlit Web应用主程序
├── futures_analyzer.py   # 核心分析引擎
├── config.py            # 系统配置文件
├── utils.py             # 工具函数模块
├── test_system.py       # 系统测试脚本
├── requirements.txt     # 依赖包列表
├── README.md           # 项目文档
└── data/               # 数据存储目录（自动创建）
```

### 主要类结构

- **FuturesAnalysisEngine**: 主分析引擎
- **FuturesDataManager**: 数据获取和管理
- **StrategyAnalyzer**: 策略分析器（支持可配置家人席位）
- **TermStructureAnalyzer**: 期限结构分析器（严格判断逻辑）
- **StreamlitApp**: Web界面应用

## 🔧 功能详解

### 1. 多空力量变化策略

**原理**: 通过分析席位持仓的增减变化来判断市场趋势

**信号判断**:
- 看多信号: 多单增加且空单减少
- 看空信号: 多单减少且空单增加
- 信号强度: 基于持仓变化幅度计算

**新增功能**:
- 支持查看每个信号的详细持仓数据
- 显示前20名席位的持仓明细
- 汇总数据展示（总多单、总空单、变化情况）

### 2. 蜘蛛网策略

**原理**: 基于持仓分布的分化程度判断机构资金的参与情况

**核心指标**:
- MSD (Mean Squared Deviation): 衡量持仓分布的分化程度
- ITS (Informed Trader Signal): 知情者信号
- UTS (Uninformed Trader Signal): 非知情者信号

**信号判断**:
- MSD > 0.05: 看多信号
- MSD < -0.05: 看空信号

**新增功能**:
- 支持查看每个信号的详细持仓数据
- 显示知情者和非知情者的持仓分布
- 详细的MSD计算过程展示

### 3. 家人席位反向操作策略

**原理**: 基于散户投资者往往在市场顶部做多、底部做空的特点

**可配置家人席位**: 
- 默认监控：东方财富、平安期货、徽商期货
- 用户可在侧边栏自定义添加或删除席位
- 支持实时更新配置

**信号判断**:
- 看多信号: 当所有家人席位的空单持仓量变化为正（增加），且多单持仓量变化为负或0（减少或不变）时
- 看空信号: 当所有家人席位的多单持仓量变化为正（增加），且空单持仓量变化为负或0（减少或不变）时
- 中性信号: 不满足上述严格条件时
- 信号强度: 基于持仓变化占总持仓的比例计算

**改进功能**:
- 清晰显示持仓变化：多单增加/减少X手，空单增加/减少X手
- 显示当前监控的家人席位配置
- 支持查看详细的席位持仓变化

### 4. 期限结构分析

**原理**: 通过比较同一品种不同交割月份合约的价格关系

**严格判断标准**:
- **Back结构**: 近月合约价格到远月合约价格严格递减
- **Contango结构**: 近月合约价格到远月合约价格严格递增
- **平坦结构**: 不符合严格递减或递增的价格关系

**改进功能**:
- 严格的期限结构判断逻辑，避免误判
- 合约按月份正确排序（从近月到远月）
- 价格信息可展开查看，不直接显示
- 显示价格变化趋势和百分比
- 区分显示不同结构类型的品种

### 5. 信号共振分析

**功能**: 识别多个策略共同看好的品种

**优势**: 提高信号可靠性，降低误判风险

**显示内容**:
- 共振看多/看空品种
- 参与策略数量和名称
- 按共振强度排序

## 🎯 使用指南

### 基本操作流程

1. **配置家人席位**
   - 在左侧边栏查看当前家人席位配置
   - 可添加新席位或删除现有席位
   - 支持重置为默认配置

2. **选择分析日期**
   - 在左侧边栏选择要分析的交易日期
   - 建议选择最近的工作日

3. **配置显示参数**
   - 设置显示数量限制
   - 选择是否显示图表

4. **开始分析**
   - 点击"开始分析"按钮
   - 等待数据获取和分析完成
   - 查看实时进度显示

5. **查看结果**
   - 浏览各策略的分析结果
   - 点击展开查看详细持仓信息
   - 查看信号共振品种
   - 分析期限结构

6. **导出报告**
   - 下载Excel格式的详细报告
   - 下载文本格式的简要报告

### 高级功能

#### 家人席位配置

- **查看当前配置**: 在侧边栏查看当前监控的家人席位
- **添加新席位**: 输入期货公司名称并点击"添加席位"
- **删除席位**: 点击席位旁边的"❌"按钮
- **重置配置**: 点击"重置为默认"恢复默认配置
- **实时生效**: 配置更改后立即生效，下次分析时使用新配置

#### 详细持仓查看

- **多空力量变化策略**: 每个信号都可展开查看详细持仓数据
- **蜘蛛网策略**: 查看知情者和非知情者的持仓分布
- **家人席位策略**: 查看家人席位的具体持仓变化
- **期限结构分析**: 展开查看合约价格详情和变化趋势

#### 缓存机制

- 系统自动缓存分析结果1小时
- 相同日期和相同家人席位配置的重复分析会使用缓存数据
- 家人席位配置变更会触发重新分析
- 可手动清除缓存强制重新分析

## 🔍 故障排除

### 常见问题

#### 1. 期限结构判断异常

**问题描述**: 期限结构判断出现错误，如eb2602大于eb2601的情况

**解决方案**:
- v2.0已修复此问题，采用严格的递减/递增判断逻辑
- 合约按月份正确排序，确保从近月到远月的顺序
- 只有严格递减的才判断为Back结构，严格递增的才判断为Contango结构

#### 2. 家人席位配置丢失

**问题描述**: 重启应用后家人席位配置丢失

**解决方案**:
- 家人席位配置存储在会话状态中
- 重启应用会恢复为默认配置
- 建议记录自定义配置，重启后重新设置

#### 3. 持仓数据显示不完整

**问题描述**: 某些合约的持仓数据显示不完整

**解决方案**:
- 检查网络连接状态
- 确认选择的日期是交易日
- 查看详细持仓信息中的原始数据

### 系统测试

运行完整的系统测试来诊断问题:

```bash
python test_system.py
```

## ⚙️ 配置说明

### 家人席位配置

在 `config.py` 中可以修改默认家人席位：

```python
STRATEGY_CONFIG = {
    "家人席位反向操作策略": {
        "enabled": True,
        "default_retail_seats": [
            "东方财富", "平安期货", "徽商期货"
        ],
    }
}
```

### 其他配置项

详见 `config.py` 文件中的各项配置说明。

## 📊 性能优化

### v2.0版本改进

| 功能 | 改进内容 |
|------|----------|
| 家人席位配置 | 支持用户自定义，实时生效 |
| 期限结构分析 | 严格判断逻辑，避免误判 |
| 持仓信息展示 | 支持展开查看详细数据 |
| 持仓变化描述 | 清晰显示增加/减少情况 |
| 缓存机制 | 考虑配置变更的智能缓存 |
| 用户体验 | 更清晰的界面和操作提示 |

## 🔄 更新日志

### v2.0 (当前版本)

**新增功能**:
- 可配置的家人席位功能
- 详细持仓信息查看功能
- 改进的期限结构分析逻辑
- 更清晰的持仓变化描述
- 作者信息和联系方式显示

**策略改进**:
- 家人席位支持用户自定义配置
- 期限结构采用严格的递减/递增判断
- 持仓变化描述更加清晰（增加/减少X手）
- 所有策略支持查看详细持仓数据

**用户体验改进**:
- 侧边栏家人席位配置界面
- 可展开的详细信息查看
- 更清晰的数据来源说明
- 改进的缓存机制

## 🤝 贡献指南

### 联系方式

- **作者**: 7haoge
- **邮箱**: 953534947@qq.com

### 反馈建议

如果您在使用过程中遇到问题或有改进建议，请：

1. 首先运行系统测试诊断问题
2. 查看本文档的故障排除部分
3. 通过邮箱联系作者
4. 提供详细的问题描述和系统测试结果

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

---

**期货持仓分析系统 v2.0** - 让期货分析更简单、更高效！

**作者：7haoge | 邮箱：953534947@qq.com** 