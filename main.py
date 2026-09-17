import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_movies.csv"
)


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 여러 장르가 "|"로 연결된 경우 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 숫자형 열 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


try:
    df = load_data()
except Exception as e:
    st.error("영화 데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
    st.stop()


# --------------------------------------------------
# 제목
# --------------------------------------------------
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

st.markdown(
    """
1년간 박스오피스 10위권에 든 영화 가운데 이 기간에 개봉한 영화들의
데이터를 살펴봅니다.
"""
)

st.divider()


# --------------------------------------------------
# 기본 데이터 요약
# --------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("영화 수", f"{len(df):,}편")

with col2:
    st.metric("장르 수", f"{df['genre'].nunique():,}개")

with col3:
    st.metric("제작 국가 수", f"{df['nation'].nunique():,}개")


st.divider()


# ==================================================
# 그래프 1. 장르별 영화 편수
# ==================================================
st.subheader("1. 장르별 영화 편수")

genre_counts = (
    df["genre"]
    .value_counts()
    .rename_axis("genre")
    .reset_index(name="count")
)

fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.48,
    title="장르별 영화 편수",
)

fig_genre.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    ),
)

fig_genre.update_layout(
    height=520,
    margin=dict(t=70, b=30, l=20, r=20),
    legend_title_text="장르",
)

st.plotly_chart(
    fig_genre,
    use_container_width=True,
    config={"displayModeBar": False},
)


# 그래프 아래 설명 영역
st.markdown("---")
st.markdown("### 이 그래프로 알 수 있는 것")
st.info(
    "여기에 장르별 영화 편수와 전체에서 차지하는 비율을 보고 "
    "알 수 있는 내용을 한 문장으로 적어 보세요."
)


st.divider()


# ==================================================
# 이후 그래프를 추가할 수 있는 자리
# ==================================================
st.subheader("2. 다음 그래프")

st.info(
    "여기에 두 번째 그래프를 추가하세요. "
    "그래프 아래에는 '이 그래프로 알 수 있는 것' 영역을 "
    "같은 방식으로 만들면 됩니다."
)


st.markdown("---")
st.markdown("### 이 그래프로 알 수 있는 것")
st.info(
    "여기에 두 번째 그래프에서 알 수 있는 내용을 한 문장으로 적어 보세요."
)


# --------------------------------------------------
# 원본 데이터
# --------------------------------------------------
st.divider()

with st.expander("📋 원본 데이터 보기"):
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
