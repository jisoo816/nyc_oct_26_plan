import folium
from geopy.geocoders import Nominatim
import streamlit as st
from streamlit_folium import st_folium
from streamlit_sortables import sort_items

st.set_page_config(
    page_title="NYC Bachelorette Trip 2026",
    page_icon="🗽",
    layout="wide",
)

# -------------------------------------------------------------
# 1. 지오코더 설정 (주소 -> 위경도 변환 캐싱)
# -------------------------------------------------------------
geolocator = Nominatim(user_agent="nyc_bachelorette_planner_v2")


@st.cache_data(show_spinner=False)
def get_coordinates(address):
    try:
        loc = geolocator.geocode(address)
        if loc:
            return [loc.latitude, loc.longitude]
    except Exception:
        pass
    return None


# -------------------------------------------------------------
# 2. 기본 장소 데이터 & 카테고리 스타일 정의
# -------------------------------------------------------------
CATEGORY_STYLE = {
    "호텔": {"emoji": "🏨", "bg": "#1E88E5"},
    "음식": {"emoji": "🍴", "bg": "#FB8C00"},
    "카페/디저트": {"emoji": "☕", "bg": "#8E24AA"},
    "콘서트/엔터": {"emoji": "🎵", "bg": "#E53935"},
    "관광/공원": {"emoji": "🌳", "bg": "#43A047"},
    "쇼핑": {"emoji": "🛍️", "bg": "#00ACC1"},
}

DEFAULT_PLACES = [
    {
        "name": "Thompson Central Park",
        "address": "119 W 56th St, New York, NY 10019",
        "desc": "숙소 & 짐 보관",
        "category": "호텔",
    },
    {
        "name": "Apollo Bagels",
        "address": "224 W 35th St, New York, NY 10001",
        "desc": "베이글 테이크아웃",
        "category": "음식",
    },
    {
        "name": "Madison Square Garden",
        "address": "4 Pennsylvania Plaza, New York, NY 10001",
        "desc": "몬스타엑스 콘서트",
        "category": "콘서트/엔터",
    },
]

if "custom_places" not in st.session_state:
    st.session_state.custom_places = DEFAULT_PLACES

# -------------------------------------------------------------
# 3. 탭 구성
# -------------------------------------------------------------
tab_schedule, tab_manage = st.tabs(
    ["🗓️ 일정 & 동선 지도", "➕ 내 장소 추가/관리"]
)

# -------------------------------------------------------------
# TAB 1: 일정표 & 드래그 앤 드롭 동선 맵
# -------------------------------------------------------------
with tab_schedule:
    col_schedule, col_map = st.columns([1.1, 1.2], gap="large")

    with col_schedule:
        st.subheader("🗓️ 동선 순서 편집 (Drag & Drop)")
        st.caption(
            "👇 마우스로 카드를 끌어서 순서를 바꾸면 오른쪽 지도의 경로와 번호가 자동으로 재정렬돼요."
        )

        # 드래그 앤 드롭 목록 항목 생성
        place_names = [p["name"] for p in st.session_state.custom_places]
        sorted_names = sort_items(place_names, direction="vertical")

        # 사용자가 드래그해서 바꾼 순서대로 세션 데이터 동기화
        st.session_state.custom_places = sorted(
            st.session_state.custom_places,
            key=lambda x: (
                sorted_names.index(x["name"])
                if x["name"] in sorted_names
                else 99
            ),
        )

        st.divider()
        st.markdown("#### 📋 1박 2일 고정 타임라인")
        st.markdown(
            """
            * **10/6 (화)**: ATL 출발(08:11 AM) ➔ EWR 도착(10:32 AM) ➔ 체크인 & K-타운 ➔ **08:00 PM 콘서트 (MSG)**
            * **10/7 (수)**: 호텔 조식 & 짐 보관 ➔ 웨스트 빌리지 투어 ➔ 짐 픽업 ➔ **06:30 PM 공항 이동**
            """
        )
        draw_line = st.checkbox("동선 연결선 지도에 표시", value=True)

    with col_map:
        st.subheader("🗺️ 저장된 동선 맵")

        # 좌표 변환 및 지도 중심 계산
        coords_list = []
        valid_items = []
        for idx, p in enumerate(st.session_state.custom_places, start=1):
            coord = get_coordinates(p["address"])
            if coord:
                coords_list.append(coord)
                valid_items.append((idx, p, coord))

        center = (
            [
                sum(c[0] for c in coords_list) / len(coords_list),
                sum(c[1] for c in coords_list) / len(coords_list),
            ]
            if coords_list
            else [40.7580, -73.9855]
        )

        m = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")

        # 커스텀 뱃지 마커 렌더링 (순서 번호 + 이모지)
        for idx, p, coord in valid_items:
            style = CATEGORY_STYLE.get(
                p["category"], {"emoji": "📍", "bg": "#333333"}
            )

            # 세련된 원형 뱃지 HTML 디자인
            marker_html = f"""
            <div style="
                background-color: {style['bg']};
                color: white;
                border: 2px solid white;
                border-radius: 20px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: bold;
                display: flex;
                align-items: center;
                gap: 4px;
                box-shadow: 0px 2px 6px rgba(0,0,0,0.4);
                white-space: nowrap;
            ">
                <span>{style['emoji']}</span>
                <span>#{idx}</span>
            </div>
            """

            folium.Marker(
                location=coord,
                tooltip=f"#{idx} {p['name']}",
                popup=folium.Popup(
                    f"<b>#{idx} {p['name']}</b><br>{p['address']}<br><i>{p['desc']}</i>",
                    max_width=250,
                ),
                icon=folium.DivIcon(html=marker_html),
            ).add_to(m)

        # 동선 점선 연결
        if draw_line and len(coords_list) > 1:
            folium.PolyLine(
                locations=coords_list,
                color="#0066cc",
                weight=3,
                opacity=0.85,
                dash_array="6, 6",
            ).add_to(m)

        st_folium(m, width="100%", height=560)

# -------------------------------------------------------------
# TAB 2: 장소 추가 및 삭제 관리
# -------------------------------------------------------------
with tab_manage:
    st.subheader("📍 새 장소 추가하기")

    with st.form("add_place_form", clear_on_submit=True):
        f_name = st.text_input(
            "장소 이름", placeholder="예: L'Industrie Pizzeria West Village"
        )
        f_address = st.text_input(
            "상세 주소",
            placeholder="예: 104 Christopher St, New York, NY 10014",
        )
        f_desc = st.text_input("메모", placeholder="예: 부라타 조각 피자 픽업")
        f_cat = st.selectbox("카테고리", list(CATEGORY_STYLE.keys()))

        submitted = st.form_submit_button("추가하기")
        if submitted:
            if not f_name or not f_address:
                st.error("장소 이름과 주소를 입력해 주세요!")
            else:
                with st.spinner("주소 확인 중..."):
                    coord = get_coordinates(f_address)
                    if coord:
                        st.session_state.custom_places.append(
                            {
                                "name": f_name,
                                "address": f_address,
                                "desc": f_desc,
                                "category": f_cat,
                            }
                        )
                        st.success(f"'{f_name}' 추가 완료!")
                        st.rerun()
                    else:
                        st.error("주소를 찾을 수 없습니다. 도로명 주소를 확인해 주세요.")

    st.divider()
    st.subheader("📋 장소 목록 삭제")
    for i, place in enumerate(st.session_state.custom_places):
        col_t, col_b = st.columns([5, 1])
        with col_t:
            st.write(
                f"**{place['name']}** ({place['category']}) - {place['address']}"
            )
        with col_b:
            if st.button("삭제", key=f"del_{i}"):
                st.session_state.custom_places.pop(i)
                st.rerun()