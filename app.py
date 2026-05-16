import json
import urllib.error
import urllib.request

import streamlit as st

FALLBACK_HUI_LV = 7.2

PLATFORM_OPTIONS = {
    "Amazon (佣金15%)": {"display": "亚马逊", "yong_jin_bili": 15.0},
    "TikTok Shop (佣金5%)": {"display": "TikTok", "yong_jin_bili": 5.0},
    "Temu (佣金0%)": {"display": "Temu", "yong_jin_bili": 0.0},
}


def fetch_usd_cny_rate():
    """从免费公开接口获取美元兑人民币汇率，失败时返回 None。"""
    sources = [
        (
            "https://api.frankfurter.app/latest?from=USD&to=CNY",
            lambda data: data["rates"]["CNY"],
        ),
        (
            "https://open.er-api.com/v6/latest/USD",
            lambda data: data["rates"]["CNY"],
        ),
    ]
    headers = {"User-Agent": "MystoreAI-ProfitCalculator/1.0"}
    for url, extract in sources:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                rate = float(extract(data))
                if rate > 0:
                    return rate
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TypeError, ValueError):
            continue
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_exchange_rate():
    """缓存汇率，减少重复请求；失败时使用保底汇率。"""
    rate = fetch_usd_cny_rate()
    if rate is None:
        return FALLBACK_HUI_LV, False
    return rate, True


def calc_profit(
    cai_gou,
    yun_fei,
    tui_huo_sun_hao,
    shou_jia_usd,
    yue_xiao_liang,
    yong_jin_bili,
    hui_lv,
):
    xiao_shou_e = shou_jia_usd * hui_lv
    ping_tai_yong_jin = xiao_shou_e * (yong_jin_bili / 100)
    zong_cheng_ben = cai_gou + yun_fei + ping_tai_yong_jin + tui_huo_sun_hao
    li_run = xiao_shou_e - zong_cheng_ben
    yue_zong_li_run = li_run * yue_xiao_liang
    mao_li_lv = (li_run / xiao_shou_e * 100) if xiao_shou_e > 0 else 0.0
    return {
        "xiao_shou_e": xiao_shou_e,
        "ping_tai_yong_jin": ping_tai_yong_jin,
        "zong_cheng_ben": zong_cheng_ben,
        "li_run": li_run,
        "mao_li_lv": mao_li_lv,
        "yue_zong_li_run": yue_zong_li_run,
    }


st.set_page_config(
    page_title="跨境卖家利润计算器",
    page_icon="💰",
    layout="wide",
)

st.title("💰 跨境卖家利润计算器")
st.caption("左右分栏实时测算 · 适合亚马逊 / TikTok / Temu 卖家")

col_input, col_report = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("📋 数据输入区")
    platform_label = st.selectbox(
        "选择销售平台",
        options=list(PLATFORM_OPTIONS.keys()),
        index=0,
    )
    platform = PLATFORM_OPTIONS[platform_label]

    cai_gou = st.number_input("产品采购价 (人民币)", min_value=0.0, value=0.0, step=1.0, format="%.2f")
    yun_fei = st.number_input("国内到海外运费 (人民币)", min_value=0.0, value=0.0, step=1.0, format="%.2f")
    tui_huo_sun_hao = st.number_input(
        "单件退货损耗成本 (人民币)", min_value=0.0, value=0.0, step=1.0, format="%.2f"
    )
    shou_jia_usd = st.number_input("拟定售价 (美金)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
    yue_xiao_liang = st.number_input("预计月销量 (件)", min_value=0, value=0, step=1)

with col_report:
    st.subheader("📊 实时利润报告区")

    hui_lv, rate_ok = get_exchange_rate()
    if rate_ok:
        st.success(f"💱 今日实时美金汇率：**{hui_lv:.4f}**（已自动联网获取）")
    else:
        st.warning(f"💱 美金汇率：**{hui_lv:.4f}**（网络获取失败，已使用保底汇率 {FALLBACK_HUI_LV}）")

    st.markdown(f"### 🏪 评估平台：{platform['display']}")

    result = calc_profit(
        cai_gou=cai_gou,
        yun_fei=yun_fei,
        tui_huo_sun_hao=tui_huo_sun_hao,
        shou_jia_usd=shou_jia_usd,
        yue_xiao_liang=yue_xiao_liang,
        yong_jin_bili=platform["yong_jin_bili"],
        hui_lv=hui_lv,
    )

    m1, m2 = st.columns(2)
    m1.metric("单件销售额 (元)", f"¥{result['xiao_shou_e']:.2f}")
    m2.metric(
        "平台佣金 (元)",
        f"¥{result['ping_tai_yong_jin']:.2f}",
        delta=f"{platform['yong_jin_bili']:.0f}%",
        delta_color="off",
    )

    m3, m4 = st.columns(2)
    m3.metric("单件总成本 (元)", f"¥{result['zong_cheng_ben']:.2f}")
    li_run_delta = "盈利" if result["li_run"] >= 0 else "亏损"
    m4.metric(
        "单件净利润 (元)",
        f"¥{result['li_run']:.2f}",
        delta=li_run_delta,
        delta_color="normal" if result["li_run"] >= 0 else "inverse",
    )

    st.metric("产品毛利率 (%)", f"{result['mao_li_lv']:.2f}%")

    if result["mao_li_lv"] > 30:
        st.success("🔥 这是一个潜力爆款！")
    elif result["mao_li_lv"] < 15:
        st.error("🚨 利润偏低，请谨慎开发")

    profit_color = "#2ecc71" if result["yue_zong_li_run"] >= 0 else "#e74c3c"
    st.markdown("---")
    st.markdown(
        f"""
        <p style="font-size: 2.4rem; font-weight: 800; color: {profit_color};
                  text-align: center; margin: 1.5rem 0;">
            🏆 预计月总利润：¥{result['yue_zong_li_run']:,.2f} 元
        </p>
        """,
        unsafe_allow_html=True,
    )
