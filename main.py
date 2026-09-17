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
# ==================================================
# 그래프 4. 개봉일 스크린 수와 총 관객의 관계
# ==================================================
st.subheader("4. 개봉일 스크린 수와 총 관객의 관계")

scatter_df = df[
    ["movieNm", "genre", "first_scrn", "total_audi"]
].copy()

scatter_df["first_scrn"] = pd.to_numeric(
    scatter_df["first_scrn"],
    errors="coerce"
)
scatter_df["total_audi"] = pd.to_numeric(
    scatter_df["total_audi"],
    errors="coerce"
)

scatter_df = scatter_df.dropna(
    subset=["movieNm", "genre", "first_scrn", "total_audi"]
)

fig_scatter = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,.0f",
        "total_audi": ":,.0f",
        "genre": True,
    },
    title="개봉일 스크린 수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "genre": "장르",
    },
    opacity=0.75,
)

fig_scatter.update_traces(
    marker=dict(size=9),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "장르: %{customdata[2]}<br>"
        "개봉일 스크린 수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    ),
)

fig_scatter.update_layout(
    height=600,
    margin=dict(t=70, b=50, l=20, r=20),
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객 수",
    legend_title_text="장르",
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True,
    config={"displayModeBar": False},
)


# 그래프 아래 설명 영역
st.markdown("---")
st.markdown("### 이 그래프로 알 수 있는 것")
st.info(
    "개봉일 스크린 수와 총 관객 수가 어떤 관계를 보이는지 "
    "점들의 분포와 장르별 색을 살펴보고 한 문장으로 적어 보세요."
)
# ==================================================
# 그래프 5. 장르별 총 관객 수 상자 그림
# ==================================================
st.subheader("5. 장르별 총 관객 수 분포")

box_df = df[
    ["movieNm", "genre", "total_audi"]
].copy()

box_df["total_audi"] = pd.to_numeric(
    box_df["total_audi"],
    errors="coerce"
)

box_df = box_df.dropna(
    subset=["movieNm", "genre", "total_audi"]
)

# 영화가 10편 이상인 장르만 선택
genre_movie_counts = box_df["genre"].value_counts()

selected_genres = genre_movie_counts[
    genre_movie_counts >= 10
].index

box_df = box_df[
    box_df["genre"].isin(selected_genres)
]


fig_box = px.box(
    box_df,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",
    hover_name="movieNm",
    hover_data={
        "genre": False,
        "total_audi": ":,.0f",
    },
    title="영화가 10편 이상인 장르의 총 관객 수 분포",
    labels={
        "genre": "장르",
        "total_audi": "총 관객 수",
    },
)

# 이상치에만 영화명이 표시되도록 설정
fig_box.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig_box.update_layout(
    height=600,
    margin=dict(t=70, b=50, l=20, r=20),
    xaxis_title="장르",
    yaxis_title="총 관객 수",
    showlegend=False,
)

st.plotly_chart(
    fig_box,
    use_container_width=True,
    config={"displayModeBar": False},
)


# 그래프 아래 설명 영역
st.markdown("---")
st.markdown("### 이 그래프로 알 수 있는 것")
st.info(
    "영화가 10편 이상인 장르들의 총 관객 수 분포와 장르별 차이를 "
    "상자와 이상치의 위치를 비교해 한 문장으로 적어 보세요."
)
# ==================================================
# 그래프 6. 개봉일 스크린 수와 총 관객 - 버블 그래프
# ==================================================
st.subheader("6. 개봉일 스크린 수와 총 관객의 관계 - 버블 그래프")

bubble_df = df[
    [
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi",
        "first_week_audi",
    ]
].copy()

for column in ["first_scrn", "total_audi", "first_week_audi"]:
    bubble_df[column] = pd.to_numeric(
        bubble_df[column],
        errors="coerce"
    )

bubble_df = bubble_df.dropna(
    subset=[
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi",
        "first_week_audi",
    ]
)

# 버블 크기에 사용할 값은 0보다 커야 함
bubble_df = bubble_df[
    bubble_df["first_week_audi"] > 0
]

fig_bubble = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    hover_data={
        "genre": True,
        "first_scrn": ":,.0f",
        "total_audi": ":,.0f",
        "first_week_audi": ":,.0f",
    },
    size_max=45,
    opacity=0.65,
    title="개봉일 스크린 수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "first_week_audi": "첫 주 관객",
        "genre": "장르",
    },
)

fig_bubble.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "장르: %{customdata[0]}<br>"
        "개봉일 스크린 수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명<br>"
        "첫 주 관객: %{marker.size:,.0f}명"
        "<extra></extra>"
    )
)

fig_bubble.update_layout(
    height=650,
    margin=dict(t=70, b=50, l=20, r=20),
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객 수",
    legend_title_text="장르",
)

st.plotly_chart(
    fig_bubble,
    use_container_width=True,
    config={"displayModeBar": False},
)


# 그래프 아래 설명 영역
st.markdown("---")
st.markdown("### 이 그래프로 알 수 있는 것")
st.info(
    "개봉일 스크린 수와 총 관객의 관계를 살펴보면서 "
    "버블 크기로 표현된 첫 주 관객 수까지 함께 비교해 보세요."
)
# ==================================================
# 그래프 7. 제작 국가 → 장르 선버스트
# ==================================================
st.subheader("7. 제작 국가와 장르의 구성")

sunburst_df = df[
    ["nation", "genre"]
].copy()

sunburst_df["nation"] = (
    sunburst_df["nation"]
    .fillna("미상")
    .astype(str)
    .str.strip()
)

sunburst_df["genre"] = (
    sunburst_df["genre"]
    .fillna("미상")
    .astype(str)
    .str.strip()
)

sunburst_df = sunburst_df[
    (sunburst_df["nation"] != "") &
    (sunburst_df["genre"] != "")
]

# 국가 → 장르 조합별 영화 편수
sunburst_counts = (
    sunburst_df
    .groupby(["nation", "genre"])
    .size()
    .reset_index(name="count")
)

fig_sunburst = px.sunburst(
    sunburst_counts,
    path=["nation", "genre"],
    values="count",
    title="제작 국가 → 장르별 영화 편수",
)

fig_sunburst.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    ),
    textinfo="label",
)

fig_sunburst.update_layout(
    height=650,
    margin=dict(t=70, b=30, l=20, r=20),
)

st.plotly_chart(
    fig_sunburst,
    use_container_width=True,
    config={"displayModeBar": False},
)


# 그래프 아래 설명 영역
st.markdown("---")
st.markdown("### 이 그래프로 알 수 있는 것")
st.info(
    "제작 국가별 영화 구성과 그 안에서 어떤 장르의 영화가 많은지를 "
    "영화 편수의 크기로 비교해 보세요."
)
