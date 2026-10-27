"""Luxe by Madiha - sales analytics dashboard.   Run with:  streamlit run app.py"""
from __future__ import annotations
import inspect, io
from itertools import count
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.data_cleaning import BAND_ORDER, DAY_ORDER, clean_data, load_raw

PLUM, ROSE = "#4A1942", "#C2185B"
SEQ = ["#4A1942", "#C2185B", "#E57399", "#F2A65A", "#8D6A9F", "#2A9D8F"]
st.set_page_config(page_title="Luxe by Madiha - Sales Dashboard", page_icon="👗", layout="wide")
st.markdown(f"""<style>
.block-container{{padding-top:1.4rem;max-width:1500px}}
.hero{{background:linear-gradient(120deg,{PLUM},{ROSE});padding:1.5rem 2rem;border-radius:18px;color:#fff;margin-bottom:1.2rem}}
.hero h1{{margin:0;font-size:2rem;color:#fff}} .hero p{{margin:.3rem 0 0;opacity:.9}}
.kpi{{background:#fff;border-radius:14px;padding:14px 18px;box-shadow:0 2px 10px rgba(0,0,0,.08);border-left:5px solid {ROSE}}}
.kpi-label{{font-size:.78rem;text-transform:uppercase;color:#6b7280}} .kpi-value{{font-size:1.7rem;font-weight:700;color:{PLUM}}}
.insight{{background:#fff5f8;border-left:5px solid {ROSE};border-radius:10px;padding:.7rem 1rem;margin-bottom:.6rem;color:{PLUM}}}
</style>""", unsafe_allow_html=True)

_k = count()
def _w(fn): 
    try: return "width" in inspect.signature(fn).parameters
    except (TypeError, ValueError): return False
def show(fig):
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, key=f"c{next(_k)}", **({"width": "stretch"} if _w(st.plotly_chart) else {"use_container_width": True}))
def show_df(d):
    st.dataframe(d, hide_index=True, **({"width": "stretch"} if _w(st.dataframe) else {"use_container_width": True}))
def kpi(label, value): return f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>'

@st.cache_data(show_spinner="Loading & cleaning data...")
def get_data():
    raw = load_raw(); clean, log = clean_data(raw); return raw, clean, log
raw, df_all, log = get_data()

def summarise(d, by):
    g = d.groupby(by, observed=True).agg(Orders=("OrderID", "count"), Revenue=("Revenue", "sum"),
        ReturnRate=("ReturnFlag", "mean"), CancelRate=("CancelFlag", "mean"), AvgDiscount=("Discount", "mean"), AvgPrice=("Price", "mean")).reset_index()
    g["ReturnRate"] *= 100; g["CancelRate"] *= 100; g["AvgDiscount"] *= 100
    return g

# ------------------------------------------------------------ filters
st.sidebar.header("Filters")
def pick(label, col): return st.sidebar.multiselect(label, sorted(df_all[col].unique()), default=sorted(df_all[col].unique()))
cats, cities, pays, srcs = pick("Category", "Category"), pick("City", "City"), pick("Payment", "Payment"), pick("Source", "Source")
dmin, dmax = df_all["Date"].min().date(), df_all["Date"].max().date()
dr = st.sidebar.date_input("Order dates", (dmin, dmax), min_value=dmin, max_value=dmax)
if len(dr) != 2: dr = (dmin, dmax)
df = df_all[df_all.Category.isin(cats) & df_all.City.isin(cities) & df_all.Payment.isin(pays) & df_all.Source.isin(srcs)
            & (df_all.Date.dt.date >= dr[0]) & (df_all.Date.dt.date <= dr[1])]

st.markdown('<div class="hero"><h1>👗 Luxe by Madiha - Sales Dashboard</h1>'
            '<p>Khaadi original dresses · analysis of orders, seasonality, customers and returns</p></div>', unsafe_allow_html=True)
st.warning("The bundled data is SAMPLE (fake) data for practice. Replace data/Luxe_Orders.xlsx with your real orders.")
if df.empty: st.error("No orders match the current filters."); st.stop()

deliv = int(df.Delivered.sum())
cols = st.columns(6)
for c, (l, v) in zip(cols, [("Orders", f"{len(df):,}"), ("Revenue (PKR)", f"{df.Revenue.sum():,.0f}"),
        ("Avg order value", f"{df.Revenue.sum() / max(deliv, 1):,.0f}"), ("Return rate", f"{df.ReturnFlag.mean() * 100:.1f}%"),
        ("Cancel rate", f"{df.CancelFlag.mean() * 100:.1f}%"), ("COD share", f"{(df.Payment == 'COD').mean() * 100:.1f}%")]):
    c.markdown(kpi(l, v), unsafe_allow_html=True)
st.write("")

def insights(d, min_group=20):
    out = []
    cat = summarise(d, "Category"); top = cat.sort_values("Revenue", ascending=False).iloc[0]
    out.append(f"Top category by revenue: **{top.Category}** with **{top.Revenue / max(cat.Revenue.sum(), 1) * 100:.0f}%** of revenue.")
    mon = summarise(d, "Month"); b = mon.sort_values("Revenue", ascending=False).iloc[0]
    out.append(f"Best month: **{b.Month:%B %Y}** ({b.Orders:.0f} orders, PKR {b.Revenue:,.0f}).")
    pay = summarise(d, "Payment"); pay = pay[pay.Orders >= min_group]
    if len(pay) > 1:
        h = pay.sort_values("ReturnRate", ascending=False).iloc[0]; l = pay.sort_values("ReturnRate").iloc[0]
        out.append(f"Highest return rate by payment: **{h.Payment}** at **{h.ReturnRate:.1f}%** vs {l.ReturnRate:.1f}% for {l.Payment}.")
    city = summarise(d[d.City != "Unknown"], "City").sort_values("Orders", ascending=False).iloc[0]
    out.append(f"Top city by orders: **{city.City}** ({city.Orders / len(d) * 100:.0f}% of orders).")
    return out

t1, t2, t3, t4, t5, t6 = st.tabs(["Overview", "Products", "Seasonality", "Customers", "Returns & payments", "Data & quality"])
with t1:
    for t in insights(df): st.markdown(f'<div class="insight">{t}</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    with a: show(px.line(summarise(df, "Month"), x="Month", y="Revenue", markers=True, title="Monthly revenue (PKR)", color_discrete_sequence=[ROSE]))
    with b: show(px.pie(df, names="Status", hole=.55, title="Order outcomes", color_discrete_sequence=SEQ))
    show(px.treemap(df[df.Delivered == 1], path=["Category", "Product"], values="Revenue", title="Revenue by category and product", color_discrete_sequence=SEQ))
with t2:
    cat = summarise(df, "Category").sort_values("Revenue")
    a, b = st.columns(2)
    with a: show(px.bar(cat, x="Revenue", y="Category", orientation="h", title="Revenue by category (PKR)", color_discrete_sequence=[PLUM]))
    with b: show(px.scatter(cat, x="AvgPrice", y="Orders", size="Revenue", text="Category", title="Price vs orders (bubble = revenue)", color_discrete_sequence=[ROSE]))
    prod = summarise(df, ["Category", "Product"]).sort_values("Revenue", ascending=False)
    show_df(prod.round(1))
with t3:
    cm = df.groupby(["Month", "Category"]).size().reset_index(name="Orders")
    show(px.bar(cm, x="Month", y="Orders", color="Category", title="Orders per month by category (Eid, wedding and sale peaks)", color_discrete_sequence=SEQ))
    wd = summarise(df, "Weekday"); wd["Weekday"] = pd.Categorical(wd.Weekday, DAY_ORDER, ordered=True)
    show(px.bar(wd.sort_values("Weekday"), x="Weekday", y="Orders", title="Orders by weekday", color_discrete_sequence=[PLUM]))
with t4:
    a, b = st.columns(2)
    with a: show(px.bar(summarise(df, "City").sort_values("Orders"), x="Orders", y="City", orientation="h", title="Orders by city", color_discrete_sequence=[PLUM]))
    with b: show(px.bar(summarise(df, "Source"), x="Source", y="Orders", title="Orders by marketing source", color_discrete_sequence=[ROSE]))
    show(px.imshow(df.pivot_table(index="City", columns="Category", values="OrderID", aggfunc="count", fill_value=0),
                   text_auto=True, aspect="auto", title="Which city buys which category", color_continuous_scale="Purples"))
with t5:
    a, b = st.columns(2)
    with a: show(px.bar(summarise(df, "Payment"), x="Payment", y="ReturnRate", title="Return rate by payment method (%)", color_discrete_sequence=[ROSE]))
    with b:
        band = summarise(df, "DiscountBand"); band["DiscountBand"] = pd.Categorical(band.DiscountBand, BAND_ORDER, ordered=True)
        show(px.bar(band.sort_values("DiscountBand"), x="DiscountBand", y="ReturnRate", hover_data=["Orders"], title="Return rate by discount band (%)", color_discrete_sequence=[PLUM]))
    st.caption("Small groups (few orders) give unreliable rates - check the Orders column before drawing conclusions. Patterns are descriptive, not proof of cause.")
    seg = summarise(df, ["Category", "Payment"]); show_df(seg[seg.Orders >= 10].sort_values("ReturnRate", ascending=False).round(1))
with t6:
    c1, c2, c3 = st.columns(3)
    c1.metric("Raw rows", f"{len(raw):,}"); c2.metric("Clean rows", f"{len(df_all):,}"); c3.metric("Rows removed", f"{len(raw) - len(df_all):,}")
    st.subheader("Cleaning log"); show_df(pd.DataFrame(log))
    st.subheader("Data explorer"); show_df(df)
    st.download_button("Download cleaned CSV", df.to_csv(index=False).encode(), "Luxe_Orders_cleaned.csv", "text/csv")
    buf = io.BytesIO()
    with pd.ExcelWriter(buf) as xw: df.to_excel(xw, index=False)
    st.download_button("Download cleaned Excel", buf.getvalue(), "Luxe_Orders_cleaned.xlsx")
