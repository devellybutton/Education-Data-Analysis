import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")
st.markdown("""
<style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)
st.title("📊 교육 운영 현황 대시보드")

DB_PATH = "survey.db"

@st.cache_data
def load_data():
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM survey_clean", con)
    con.close()
    return df

df = load_data()

# 사이드바 필터
with st.sidebar:
    st.header("필터")
    # 회차
    all_rounds = sorted(df["회차"].unique())
    round_options = ["전체"] + all_rounds
    selected_rounds = st.multiselect("회차 선택", round_options, default=["전체"])

    if "전체" in selected_rounds:
        filtered_rounds = all_rounds
    else:
        filtered_rounds = selected_rounds

    # 직무
    all_jobs = sorted(df["직무"].unique())
    job_options = ["전체"] + all_jobs
    selected_jobs = st.multiselect("직무 선택", job_options, default=["전체"])

    if "전체" in selected_jobs:
        filtered_jobs = all_jobs
    else:
        filtered_jobs = selected_jobs

    # 엑셀 사용 경력
    all_exp = sorted(df["엑셀사용경력"].unique())
    exp_options = ["전체"] + all_exp
    selected_exp = st.multiselect("엑셀 사용 경력", exp_options, default=["전체"])

    if "전체" in selected_exp:
        filtered_exp = all_exp
    else:
        filtered_exp = selected_exp

# 필터 적용
df = df[
    (df["회차"].isin(filtered_rounds)) &
    (df["직무"].isin(filtered_jobs)) &
    (df["엑셀사용경력"].isin(filtered_exp))
]

if len(df) == 0:
    st.warning("선택 조건에 해당하는 데이터가 없습니다.")
    st.stop()

# 향상폭 계산
df["difference"] = df["사후_평균"] - df["사전_평균"]

# KPI
pre_mean = df["사전_평균"].mean()
post_mean = df["사후_평균"].mean()
overall_sat = post_mean
diff_mean = df["difference"].mean()
n = len(df)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("응답자 수", f"{n}명")
col2.metric("전체 만족도", f"{overall_sat:.2f} / 5")
col3.metric("사전 평균", f"{pre_mean:.2f}")
col4.metric("사후 평균", f"{post_mean:.2f}")
col5.metric("평균 향상폭", f"{diff_mean:.2f}")

st.markdown("---")

# 회차별 만족도
col_left, col_right = st.columns([5,5])

with col_left:
    st.subheader("1. 회차별 평균 만족도")

    round_sat = (
        df.groupby("회차")["사후_평균"]
        .mean()
        .reset_index()
        .sort_values("회차")
    )

    fig1 = px.bar(
        round_sat,
        x="회차",
        y="사후_평균",
        text=round_sat["사후_평균"].round(2),
        color="사후_평균",
        color_continuous_scale="Blues"
    )

    fig1.update_traces(textposition="outside")
    fig1.update_layout(yaxis_range=[0,5], showlegend=False)

    st.plotly_chart(fig1, use_container_width=True)

# 사전 vs 사후 평균 비교
with col_right:
    st.subheader("2. 교육 전·후 평균 비교")

    compare_df = pd.DataFrame({
        "구분": ["사전 평균", "사후 평균"],
        "점수": [pre_mean, post_mean]
    })

    fig2 = px.bar(
        compare_df,
        x="구분",
        y="점수",
        text=compare_df["점수"].round(2),
        color="구분"
    )

    fig2.update_traces(textposition="outside")
    fig2.update_layout(yaxis_range=[0,5], showlegend=False)

    st.plotly_chart(fig2, use_container_width=True)