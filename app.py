import folium
from geopy.geocoders import Nominatim
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="NYC Bachelorette Trip 2026",
    page_icon="🗽",
    layout="wide",
)

# -------------------------------------------------------------
# 1. 지오코더 설정 (주소 -> 위경도 자동 변환 캐싱)
# -------------------------------------------------------------
geolocator = Nominatim(user_agent="nyc_bachelorette_planner")


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
# 2. 세션 상태 초기화 (주소 기반 기본 목록)
# -------------------------------------------------------------
DEFAULT_CUSTOM_PLACES = [
    {
        "name": "Thompson Central Park",
        "address": "119 W 56th St, New York, NY 10019",
        "desc": "호텔 / 짐 보관",
        "category": "호텔 (침대)",
        "order": 1,
    },
    {
        "name": "Apollo Bagels",
        "address": "224 W 35th St, New York, NY 10001",
        "desc": "아침 베이글 픽업",
        "category": "음식 (포크/나이프)",
        "order": 2,
    },
    {
        "name": "Madison Square Garden",
        "address": "4 Pennsylvania Plaza, New York, NY 10001",
        "desc": "몬스타엑스 콘서트",
        "category": "콘서트/엔터 (음표)",
        "order": 3,
    },
]

if "custom_places" not in st.session_state:
    st.session_state.custom_places = DEFAULT_CUSTOM_PLACES

ICON_MAPPING = {
    "음식 (포크/나이프)": {"icon": "cutlery", "color": "orange"},
    "카페/디저트 (커피잔)": {"icon": "glass", "color": "purple"},
    "호텔 (침대)": {"icon": "bed", "color": "blue"},
    "콘서트/엔터 (음표)": {"icon": "music", "color": "red"},
    "관광/공원 (나무)": {"icon": "tree-conifer", "color": "green"},
    "쇼핑 (쇼핑백)": {"icon": "shopping-cart", "color": "cadetblue"},
}

# -------------------------------------------------------------
# 3. 메인 화면 탭 구성
# -------------------------------------------------------------
tab_schedule, tab_manage = st.tabs(
    ["🗓️ 일정 & 동선 지도", "➕ 내 장소 추가/관리"]
)

# -------------------------------------------------------------
# TAB 2: 장소 추가 및 관리 (세컨드 페이지 역할)
# -------------------------------------------------------------
with tab_manage:
    st.subheader("📍 주소로 새 장소 추가하기")
    st.caption(
        "위도/경도 필요 없이 미국 내 주소나 유명 장소 이름을 영문으로 넣으시면 자동으로 지도에 뜹니다."
    )

    with st.form("add_place_form", clear_on_submit=True):
        f_name = st.text_input(
            "장소 이름", placeholder="예: L'Industrie Pizzeria West Village"
        )
        f_address = st.text_input(
            "주소 (또는 상세 명칭)",
            placeholder="예: 104 Christopher St, New York, NY 10014",
        )
        f_desc = st.text_input(
            "메모 / 노트", placeholder="예: 부라타 조각 피자 테이크아웃"
        )

        c1, c2 = st.columns(2)
        with c1:
            f_cat = st.selectbox("카테고리 (아이콘)", list(ICON_MAPPING.keys()))
        with c2:
            f_order = st.number_input(
                "방문 순서 번호 (숫자)",
                min_value=1,
                max_value=30,
                value=len(st.session_state.custom_places) + 1,
            )

        submitted = st.form_submit_button("장소 추가하기")
        if submitted:
            if not f_name or not f_address:
                st.error("장소 이름과 주소를 모두 입력해 주세요!")
            else:
                with st.spinner("주소 위치 확인 중..."):
                    coord = get_coordinates(f_address)
                    if coord:
                        st.session_state.custom_places.append(
                            {
                                "name": f_name,
                                "address": f_address,
                                "desc": f_desc,
                                "category": f_cat,
                                "order": f_order,
                            }
                        )
                        st.success(
                            f"'{f_name}' 추가 완료! (위치 확인: {coord[0]:.4f}, {coord[1]:.4f})"
                        )
                    else:
                        st.error(
                            "입력하신 주소의 위치를 찾지 못했습니다. 주소를 더 구체적으로 적어주세요."
                        )

    st.divider()
    st.subheader("📋 현재 등록된 장소 목록")

    # 순서 번호 기준 정렬
    st.session_state.custom_places = sorted(
        st.session_state.custom_places, key=lambda x: x["order"]
    )

    for i, place in enumerate(st.session_state.custom_places):
        col_info, col_del = st.columns([5, 1])
        with col_info:
            st.markdown(
                f"**#{place['order']}. {place['name']}** [{place['category']}]  \n"
                f"📍 {place['address']} | 📝 {place['desc']}"
            )
        with col_del:
            if st.button("삭제", key=f"del_{i}"):
                st.session_state.custom_places.pop(i)
                st.rerun()

# -------------------------------------------------------------
# TAB 1: 일정 & 지도 화면
# -------------------------------------------------------------
with tab_schedule:
    col_schedule, col_map = st.columns([1, 1.2], gap="large")

    with col_schedule:
        st.subheader("🗓️ 전체 일정 타임라인")
        st.markdown(
            """
            * **10/6 (화)**
                - **08:11 AM** ATL 출발 ➔ **10:32 AM** EWR 도착 (Frontier #2282)
                - 호텔 체크인 & 짐 보관 ➔ K-타운 점심 ➔ 센트럴 파크
                - 저녁 식사 ➔ **08:00 PM 메디슨 스퀘어 가든 (몬스타엑스 콘서트)**
            * **10/7 (수)**
                - 호텔 조식 후 체크아웃 & **호텔 짐 보관**
                - 아폴로 베이글 픽업 ➔ 웨스트 빌리지 투어
                - 호텔 복귀 후 짐 픽업 ➔ **06:30 PM 공항 이동**
                - **10:29 PM** EWR 출발 ➔ **01:01 AM** ATL 도착 (Frontier #1157)
            """
        )

        st.divider()
        draw_line = st.checkbox("동선 연결선(경로) 지도에 표시하기", value=True)

    with col_map:
        st.subheader("🗺️ 저장된 동선 맵")

        # 장소 목록을 순서대로 정렬
        sorted_places = sorted(
            st.session_state.custom_places, key=lambda x: x["order"]
        )

        # 지도 중심점 계산용
        coords_list = []
        valid_places = []
        for p in sorted_places:
            coord = get_coordinates(p["address"])
            if coord:
                coords_list.append(coord)
                valid_places.append((p, coord))

        center = (
            [
                sum(c[0] for c in coords_list) / len(coords_list),
                sum(c[1] for c in coords_list) / len(coords_list),
            ]
            if coords_list
            else [40.7580, -73.9855]
        )

        m = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")

        # 마커 찍기
        for p, coord in valid_places:
            cat_info = ICON_MAPPING.get(
                p["category"], {"icon": "info-sign", "color": "blue"}
            )
            popup_html = f"""
            <b>#{p['order']} {p['name']}</b><br>
            <i>{p['category']}</i><br>
            {p['address']}<br>
            <b>Note:</b> {p['desc']}
            """
            folium.Marker(
                location=coord,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"#{p['order']} {p['name']}",
                icon=folium.Icon(
                    color=cat_info["color"], icon=cat_info["icon"]
                ),
            ).add_to(m)

        # 점선 연결
        if draw_line and len(coords_list) > 1:
            folium.PolyLine(
                locations=coords_list,
                color="#0066cc",
                weight=3,
                opacity=0.8,
                dash_array="6, 6",
            ).add_to(m)

        st_folium(m, width="100%", height=550)