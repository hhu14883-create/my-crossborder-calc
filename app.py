import streamlit as st
import requests

# ========================================================
# 📢 商业化配置中心（在这里输入你的真实信息）
# ========================================================
DRIVE_DOCUMENT_URL = "https://www.baidu.com"  # 👈 以后把你整理的干货文档链接贴在这里！

# 设置网页全屏布局
st.set_page_config(page_title="跨境电商多平台利润计算器", page_icon="📊", layout="centered")

# 用自定义 CSS 彻底汉化一些 Streamlit 自带的英文组件并美化界面
st.markdown("""
    <style>
    /* 隐藏 Streamlit 官方菜单和页脚 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 调整输入框样式 */
    .stNumberInput div div input {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 👑 网页大标题
st.title("📊 跨境电商多平台利润快速测算器")
st.write("告别繁琐 Excel · 实时自动联网汇率")
st.write("---")

# 🌐 第一部分：汇率与福利区
# 联网获取实时汇率（如果失败则使用保底汇率 6.8）
try:
    response = requests.get("https://open.er-api.com/v6/latest/USD")
    exchange_rate = response.json()["rates"]["CNY"]
    st.success(f"📈 今日实时美金汇率：{exchange_rate:.4f} （已成功自动联网获取）")
except:
    exchange_rate = 6.8
    st.warning(f"⚠️ 联网获取汇率失败，已启用保底汇率：{exchange_rate}")

# ⚡ 纯福利按钮：直接变身干货赠送通道，疯狂刷好评！
st.link_button("💡 绝密干货：各大跨境平台【真实扣费佣金表】与运营避坑指南（点击免费查看）", DRIVE_DOCUMENT_URL)
st.write("---")

# 📥 第二部分：全中文输入区（全部移到正中间，方便操作）
st.header("📥 第一步：输入产品数据")

# 平台选择
platform = st.selectbox("1. 选择你经营的销售平台", ["Amazon 亚马逊 (佣金15%)", "TikTok 趣淘 (佣金5%)", "Temu 特木 (佣金0%)"])

# 根据平台设定佣金比例
if "Amazon" in platform:
    commission_rate = 0.15
    p_name = "亚马逊"
elif "TikTok" in platform:
    commission_rate = 0.05
    p_name = "TikTok"
else:
    commission_rate = 0.00
    p_name = "Temu"

# 并排输入框，空间利用率更高
col_in1, col_in2 = st.columns(2)
with col_in1:
    cost_price = st.number_input("2. 产品采购成本 (人民币/件)", min_value=0.0, value=0.0, step=1.0)
    shipping_fee = st.number_input("3. 头程及海外运费 (人民币/件)", min_value=0.0, value=0.0, step=1.0)

with col_in2:
    sale_price_usd = st.number_input("4. 拟定海外售价 (美金/件)", min_value=0.0, value=0.0, step=0.1)
    return_cost = st.number_input("5. 预估退货与损耗 (人民币/件，可选)", min_value=0.0, value=0.0, step=1.0)

st.write("---")

# 📈 第三部分：实时利润报告区
st.header(f"📊 第二步：{p_name} 平台利润评估报告")

# 计算逻辑
sale_price_cny = sale_price_usd * exchange_rate  # 单件销售额
platform_commission = sale_price_cny * commission_rate  # 平台佣金
total_cost_cny = cost_price + shipping_fee + return_cost  # 单件总成本
net_profit_cny = sale_price_cny - platform_commission - total_cost_cny  # 单件净利润

# 计算毛利率
if sale_price_cny > 0:
    margin = (net_profit_cny / sale_price_cny) * 100
else:
    margin = 0.0

# 报告结果展示
col_res1, col_res2 = st.columns(2)
with col_res1:
    st.metric(label="💰 折算人民币销售额", value=f"¥{sale_price_cny:.2f}")
    st.metric(label="📉 平台预计扣除佣金", value=f"¥{platform_commission:.2f} ({commission_rate*100:.0f}%)")

with col_res2:
    st.metric(label="📦 运营总成本 (含采购/运费/损耗)", value=f"¥{total_cost_cny:.2f}")
    if net_profit_cny > 0:
        st.metric(label="🔥 预计单件净利润", value=f"¥{net_profit_cny:.2f}", delta="盈利状态")
    else:
        st.metric(label="🚨 预计单件净利润", value=f"¥{net_profit_cny:.2f}", delta="亏损/保本" if net_profit_cny < 0 else "保本", delta_color="inverse")

# 展现核心毛利率
st.subheader("💡 最终测算产品毛利率")
st.title(f"{margin:.2f}%")

# ⚠️ 核心功能：利润风控提示与炫酷气球特效
if sale_price_usd > 0:
    if margin < 15.0:
        st.error("🚨 警告：该产品利润率偏低，请谨慎开发，谨防卷入价格战！")
    elif margin >= 15.0:
        st.balloons()  # 满屏飞气球特效
        st.success("🎉 恭喜：该产品利润指标达标，具备打造潜力爆款的品相！")