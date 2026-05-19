import streamlit as st

# 探测是不是谷歌爬虫来要地图了
# 这一段要放在 st.title() 等任何页面渲染之前
query_params = st.query_params
if "page" in query_params and query_params["page"] == "sitemap":
    st.text("""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://hhu-calc.streamlit.app/</loc>
    <lastmod>2026-05-19</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>""")
    st.stop() # 停止渲染后面的精美界面，直接把这张纯文本地图吐给谷歌import streamlit as st
import requests

# 设置网页全屏布局
st.set_page_config(page_title="跨境电商多平台利润计算器", page_icon="📊", layout="centered")

# 用自定义 CSS 隐藏干扰组件，美化输入框
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stNumberInput div div input {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 👑 网页大标题（砍掉口水话，极致干净）
st.title("📊 跨境电商多平台利润快速测算器")
st.write("---")

# 🌐 第一部分：实时汇率区
try:
    response = requests.get("https://open.er-api.com/v6/latest/USD")
    exchange_rate = response.json()["rates"]["CNY"]
    st.success(f"📈 今日实时美金汇率：{exchange_rate:.4f} （已成功自动联网获取）")
except:
    exchange_rate = 6.8
    st.warning(f"⚠️ 联网获取汇率失败，已启用保底汇率：{exchange_rate}")

st.write("---")

# 📥 第二部分：全中文输入区
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

# 并排输入框，操作更紧凑
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
    if sale_price_usd == 0:
        st.metric(label="📊 预计单件净利润", value="¥0.00", delta="等待输入数据")
    elif net_profit_cny > 0:
        st.metric(label="🔥 预计单件净利润", value=f"¥{net_profit_cny:.2f}", delta="盈利状态")
    else:
        st.metric(label="🚨 预计单件净利润", value=f"¥{net_profit_cny:.2f}", delta="亏损状态" if net_profit_cny < 0 else "保本状态", delta_color="inverse")

# 展现核心毛利率
st.subheader("💡 最终测算产品毛利率")

# ----------------------------------------------------
# 🚨 强化版：亮点突出与风控提醒逻辑
# ----------------------------------------------------
if sale_price_usd == 0:
    st.title("0.00%")
    st.info("💡 请在上方输入产品数据，系统将自动为您评估利润风险...")
else:
    if margin >= 15.0:
        st.markdown(f"<h1 style='color: #2ecc71;'>{margin:.2f}%</h1>", unsafe_allow_html=True)
        st.balloons()  # 满屏飞气球特效
        st.success(f"🎉 利润达标！该产品在 {p_name} 平台的毛利率表现极其优秀，具备打造潜力爆款的品相，建议加大力度开发！")
    elif 0 <= margin < 15.0:
        st.markdown(f"<h1 style='color: #f39c12;'>{margin:.2f}%</h1>", unsafe_allow_html=True)
        st.warning("⚠️ 风险提示：产品虽然微利，但利润率低于 15% 的行业安全线。扣除后续广告引流、测评等隐形成本后极易亏损，请谨慎开发！")
    else:
        st.markdown(f"<h1 style='color: #e74c3c;'>{margin:.2f}%</h1>", unsafe_allow_html=True)
        st.error(f"🚨 严重警告：该产品当前定价处于【绝对亏损】状态！每卖出一件都在倒贴钱，请立刻重新调整海外售价或死磕供应链压低成本！")
