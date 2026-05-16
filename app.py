import streamlit as st
import requests

# ========================================================
# 📢 商业化配置中心（奶爸可以在这里直接修改你的信息！）
# ========================================================
AUTHOR_WECHAT = "YZ19157696431"  # 👈 快把双引号里的字改成你真正的微信号！
SETTLEMENT_PROMO_URL = "https://www.baidu.com"  # 优惠通道链接（暂时跳百度）

# 设置网页标题和图标
st.set_page_config(page_title="跨境电商多平台利润计算器", page_icon="📊", layout="wide")

# ========================================================
# 🏪 左侧边栏：数据输入区
# ========================================================
with st.sidebar:
    st.header("📋 数据输入区")
    st.write("左右分栏实时测算 · 适合亚马逊 / TikTok / Temu 卖家")
    st.write("---")
    
    # 平台选择
    platform = st.selectbox("选择销售平台", ["Amazon (佣金15%)", "TikTok (佣金5%)", "Temu (佣金0%)"])
    
    # 根据平台设定佣金比例
    if "Amazon" in platform:
        commission_rate = 0.15
    elif "TikTok" in platform:
        commission_rate = 0.05
    else:
        commission_rate = 0.00
        
    # 输入框
    cost_price = st.number_input("产品采购价 (人民币)", min_value=0.0, value=0.0, step=1.0)
    shipping_fee = st.number_input("国内到海外运费 (人民币)", min_value=0.0, value=0.0, step=1.0)
    return_cost = st.number_input("单件退货损耗成本 (人民币)", min_value=0.0, value=0.0, step=1.0)
    sale_price_usd = st.number_input("拟定售价 (美金)", min_value=0.0, value=0.0, step=0.1)
    monthly_sales = st.number_input("预计月销量 (件)", min_value=0, value=0, step=10)

    # ----------------------------------------------------
    # 🔥 黄金引流钩子：左侧边栏最下方
    # ----------------------------------------------------
    st.write("---")
    st.markdown("### 🚀 跨境老鸟带路（独立开发）")
    st.markdown(f"欢迎加入 **【跨境卖家互助搞钱群】**！群内免费分享各大平台最新避坑指南、精选货代资源。")
    st.info(f"📌 **加作者微信：{AUTHOR_WECHAT}**\n\n备注：计算器")

# ========================================================
# 📈 右侧主面板：实时利润报告区
# ========================================================
st.title("📊 实时利润报告区")

# 联网获取实时汇率（如果失败则使用保底汇率 6.8）
try:
    response = requests.get("https://open.er-api.com/v6/latest/USD")
    exchange_rate = response.json()["rates"]["CNY"]
    st.success(f"💱 今日实时美金汇率：{exchange_rate:.4f} （已自动联网获取）")
except:
    exchange_rate = 6.8
    st.warning(f"⚠️ 联网获取汇率失败，已启用保底汇率：{exchange_rate}")

# ----------------------------------------------------
# 金色高亮提示按钮（收款商联盟优惠）
# ----------------------------------------------------
st.link_button("💡 专属福利：嫌结汇手续费太贵？点击使用专属绿色通道，结汇手续费终身尊享特惠折扣！", SETTLEMENT_PROMO_URL)
st.write("---")

st.header(f"🏪 评估平台：{platform.split(' ')[0]}")

# 计算逻辑
sale_price_cny = sale_price_usd * exchange_rate  # 单件销售额（人民币）
platform_commission = sale_price_cny * commission_rate  # 平台佣金（人民币）
total_cost_cny = cost_price + shipping_fee + return_cost  # 单件总成本（人民币）
net_profit_cny = sale_price_cny - platform_commission - total_cost_cny  # 单件净利润（人民币）

# 计算毛利率
if sale_price_cny > 0:
    margin = (net_profit_cny / sale_price_cny) * 100
else:
    margin = 0.0

# 界面展示结果
col1, col2 = st.columns(2)
with col1:
    st.metric(label="单件销售额 (元)", value=f"¥{sale_price_cny:.2f}")
    st.metric(label="单件总成本 (元)", value=f"¥{total_cost_cny:.2f}")

with col2:
    st.metric(label="平台佣金 (元)", value=f"¥{platform_commission:.2f}", delta=f"{commission_rate*100:.0f}%")
    if net_profit_cny > 0:
        st.metric(label="单件净利润 (元)", value=f"¥{net_profit_cny:.2f}", delta="盈利")
    else:
        st.metric(label="单件净利润 (元)", value=f"¥{net_profit_cny:.2f}", delta="亏损" if net_profit_cny < 0 else "保本", delta_color="inverse")

st.subheader(f"产品毛利率 (%)")
st.title(f"{margin:.2f}%")

# 利润风控提示
if margin < 15.0 and sale_price_usd > 0:
    st.error("🚨 利润偏低，请谨慎开发！")
elif margin >= 15.0:
    st.balloons()
    st.success("🔥 这是一个潜力爆款，利润达标！")