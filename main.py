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
# ==================================================
# 그래프 2. 장르별 영화 트리맵
# ==================================================
st.subheader("2. 장르 안에 들어 있는 영화")

treemap_df = df[
    ["genre", "movieNm", "total_audi"]
].dropna(subset=["genre", "movieNm", "total_audi"]).copy()

treemap_df["total_audi"] = pd.to_numeric(
    treemap_df["total_audi"],
    errors="coerce"
)

treemap_df = treemap_df[treemap_df["total_audi"] > 0]

fig_treemap = px.treemap(
    treemap_df,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화와 총 관객",
)

fig_treemap.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    ),
    textinfo="label",
)

fig_treemap.update_layout(
    height=650,
    margin=dict(t=70, b=30, l=20, r=20),
)

st.plotly_chart(
    fig_treemap,
    use_container_width=True,
    config={"displayModeBar": False},
)


# 그래프 아래 설명 영역
st.markdown("---")
st.markdown("### 이 그래프로 알 수 있는 것")
st.info(
    "여기에 장르별로 어떤 영화가 많은 관객을 모았는지 "
    "트리맵의 크기를 보고 알 수 있는 내용을 한 문장으로 적어 보세요."
)
# ==================================================
# 그래프 3. 총 관객 수 히스토그램
# ==================================================
st.subheader("3. 총 관객 수의 분포")

hist_df = df[["movieNm", "total_audi"]].copy()
hist_df["total_audi"] = pd.to_numeric(
    hist_df["total_audi"],
    errors="coerce"
)
hist_df = hist_df.dropna(subset=["total_audi"])

fig_hist = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 수 분포",
    labels={
        "total_audi": "총 관객 수",
        "count": "영화 편수",
    },
)

fig_hist.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig_hist.update_layout(
    height=500,
    margin=dict(t=70, b=50, l=20, r=20),
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수",
)

st.plotly_chart(
    fig_hist,
    use_container_width=True,
    config={"displayModeBar": False},
)


# --------------------------------------------------
# 가장 관객이 많은 영화
# --------------------------------------------------
most_watched = hist_df.loc[
    hist_df["total_audi"].idxmax()
]

max_movie_name = most_watched["movieNm"]
max_audience = int(most_watched["total_audi"])

# 가장 많은 영화가 포함된 히스토그램 구간
hist_counts, bin_edges = pd.cut(
    hist_df["total_audi"],
    bins=20,
    include_lowest=True,
    retbins=True,
)

bin_counts = hist_counts.value_counts().sort_index()
most_common_bin = bin_counts.idxmax()

lower_bound = int(most_common_bin.left)
upper_bound = int(most_common_bin.right)

st.markdown("---")
st.markdown("### 이 그래프로 알 수 있는 것")

st.info(
    f"대부분의 영화는 총 관객 수 **{lower_bound:,}명~{upper_bound:,}명** "
    f"구간에 몰려 있으며, 가장 관객이 많은 영화는 "
    f"**{max_movie_name}**으로 총 **{max_audience:,}명**의 관객을 기록했습니다."
)
