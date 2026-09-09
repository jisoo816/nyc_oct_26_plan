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
# 1. 지오코더 설정
# -------------------------------------------------------------
geolocator = Nominatim(user_agent="nyc_bachelorette_planner_v5")


@st.cache_data(show_spinner=False)
def get_coordinates(address):
    try:
        loc = geolocator.geocode(address)
        if loc:
            return [loc.latitude, loc.longitude]
    except Exception:
        pass
    return None


CATEGORY_STYLE = {
    "호텔": {"emoji": "🏨", "bg": "#1E88E5"},
    "음식": {"emoji": "🍴", "bg": "#FB8C00"},
    "카페/디저트": {"emoji": "☕", "bg": "#8E24AA"},
    "콘서트/엔터": {"emoji": "🎵", "bg": "#E53935"},
    "관광/공원": {"emoji": "🌳", "bg": "#43A047"},
    "쇼핑": {"emoji": "🛍️", "bg": "#00ACC1"},
}

# -------------------------------------------------------------
# 2. 세션 상태 초기화: [장소 풀]과 [일정표 슬롯] 분리
# -------------------------------------------------------------
if "place_pool" not in st.session_state:
    st.session_state.place_pool = {
        "Thompson Central Park": {
            "address": "119 W 56th St, New York, NY 10019",
            "category": "호텔",
        },
        "Apollo Bagels": {
            "address": "224 W 35th St, New York, NY 10001",
            "category": "음식",
        },
        "Madison Square Garden": {
            "address": "4 Pennsylvania Plaza, New York, NY 10001",
            "category": "콘서트/엔터",
        },
        "EWR Airport": {
            "address": "3 Brewster Rd, Newark, NJ 07114",
            "category": "관광/공원",
        },
    }

if "schedule_rows" not in st.session_state:
    st.session_state.schedule_rows = [
        {
            "time": "12:00 PM",
            "place": "Thompson Central Park",
            "note": "체크인 & 짐 보관",
        },
        {"time": "02:00 PM", "place": "Apollo Bagels", "note": "베이글 테이크아웃"},
        {
            "time": "07:30 PM",
            "place": "Madison Square Garden",
            "note": "몬스타엑스 콘서트",
        },
    ]

# -------------------------------------------------------------
# 3. 탭 구성
# -------------------------------------------------------------
tab_main, tab_places = st.tabs(["🗓️ 일정표 & 동선 지도", "📍 등록된 장소 풀 관리"])

# -------------------------------------------------------------
# TAB 1: 일정표 (자유로운 행 추가/삭제/장소 지정) + 지도
# -------------------------------------------------------------
with tab_main:
    col_schedule, col_map = st.columns([1.3, 1.1], gap="large")

    with col_schedule:
        st.subheader("📋 일정표 편집")
        st.caption(
            "각 순번마다 시간, 장소(선택), 노트를 입력하세요. 위/아래 이동 및 행 추가가 자유롭습니다."
        )

        place_options = ["(장소 없음)"] + list(st.session_state.place_pool.keys())

        # 일정 행 렌더링
        for idx, row_data in enumerate(st.session_state.schedule_rows):
            with st.container(border=True):
                c_num, c_time, c_place, c_up, c_down, c_del = st.columns(
                    [0.8, 1.5, 2.8, 0.6, 0.6, 0.6]
                )

                with c_num:
                    st.markdown(f"### #{idx + 1}")

                with c_time:
                    new_time = st.text_input(
                        "시간",
                        value=row_data["time"],
                        key=f"time_{idx}",
                        placeholder="12:00 PM",
                    )
                    st.session_state.schedule_rows[idx]["time"] = new_time

                with c_place:
                    current_p = (
                        row_data["place"]
                        if row_data["place"] in place_options
                        else "(장소 없음)"
                    )
                    selected_p = st.selectbox(
                        "장소 지정",
                        options=place_options,
                        index=place_options.index(current_p),
                        key=f"place_{idx}",
                    )
                    st.session_state.schedule_rows[idx]["place"] = selected_p

                with c_up:
                    st.write("")
                    st.write("")
                    if st.button("▲", key=f"up_{idx}", help="위로 이동"):
                        if idx > 0:
                            (
                                st.session_state.schedule_rows[idx - 1],
                                st.session_state.schedule_rows[idx],
                            ) = (
                                st.session_state.schedule_rows[idx],
                                st.session_state.schedule_rows[idx - 1],
                            )
                            st.rerun()

                with c_down:
                    st.write("")
                    st.write("")
                    if st.button("▼", key=f"down_{idx}", help="아래로 이동"):
                        if idx < len(st.session_state.schedule_rows) - 1:
                            (
                                st.session_state.schedule_rows[idx + 1],
                                st.session_state.schedule_rows[idx],
                            ) = (
                                st.session_state.schedule_rows[idx],
                                st.session_state.schedule_rows[idx + 1],
                            )
                            st.rerun()

                with c_del:
                    st.write("")
                    st.write("")
                    if st.button("✖", key=f"del_row_{idx}", help="행 삭제"):
                        st.session_state.schedule_rows.pop(idx)
                        st.rerun()

                # 노트 입력 칸
                new_note = st.text_input(
                    "활동 내용 / 노트",
                    value=row_data["note"],
                    key=f"note_{idx}",
                    placeholder="세부 메모를 적어주세요",
                )
                st.session_state.schedule_rows[idx]["note"] = new_note

        # 행 추가 버튼
        if st.button("➕ 새로운 일정 행 추가하기", use_container_width=True):
            st.session_state.schedule_rows.append(
                {"time": "", "place": "(장소 없음)", "note": ""}
            )
            st.rerun()

        st.divider()
        draw_line = st.checkbox("지도에 경로 점선 연결하기", value=True)

    # 우측 지도 렌더링
    with col_map:
        st.subheader("🗺️ 실시간 동선 맵")

        coords_list = []
        map_points = []

        # 일정표에 매핑된 장소들을 순서대로 추출
        for idx, row in enumerate(st.session_state.schedule_rows, start=1):
            p_name = row["place"]
            if p_name != "(장소 없음)" and p_name in st.session_state.place_pool:
                p_info = st.session_state.place_pool[p_name]
                coord = get_coordinates(p_info["address"])
                if coord:
                    coords_list.append(coord)
                    map_points.append(
                        {
                            "seq": idx,
                            "name": p_name,
                            "time": row["time"],
                            "note": row["note"],
                            "category": p_info["category"],
                            "address": p_info["address"],
                            "coord": coord,
                        }
                    )

        center = (
            [
                sum(c[0] for c in coords_list) / len(coords_list),
                sum(c[1] for c in coords_list) / len(coords_list),
            ]
            if coords_list
            else [40.7580, -73.9855]
        )

        m = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")

        for pt in map_points:
            style = CATEGORY_STYLE.get(
                pt["category"], {"emoji": "📍", "bg": "#333333"}
            )
            marker_html = f"""
            <div style="
                background-color: {style['bg']};
                color: white;
                border: 2px solid white;
                border-radius: 18px;
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
                <span>#{pt['seq']}</span>
            </div>
            """
            popup_html = f"""
            <b>#{pt['seq']}. {pt['name']}</b><br>
            <b>시간:</b> {pt['time']}<br>
            <b>주소:</b> {pt['address']}<br>
            <b>노트:</b> {pt['note']}
            """
            folium.Marker(
                location=pt["coord"],
                tooltip=f"#{pt['seq']} {pt['name']}",
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.DivIcon(html=marker_html),
            ).add_to(m)

        if draw_line and len(coords_list) > 1:
            folium.PolyLine(
                locations=coords_list,
                color="#0066cc",
                weight=3,
                opacity=0.85,
                dash_array="6, 6",
            ).add_to(m)

        st_folium(m, width="100%", height=600)

# -------------------------------------------------------------
# TAB 2: 장소 보관함(풀) 추가 및 관리
# -------------------------------------------------------------
with tab_places:
    st.subheader("📍 사용할 수 있는 장소 등록하기")

    with st.form("add_pool_form", clear_on_submit=True):
        new_name = st.text_input(
            "장소 이름", placeholder="예: L'Industrie Pizzeria"
        )
        new_addr = st.text_input(
            "상세 주소",
            placeholder="예: 104 Christopher St, New York, NY 10014",
        )
        new_cat = st.selectbox("카테고리 아이콘", list(CATEGORY_STYLE.keys()))

        if st.form_submit_button("장소 보관함에 추가"):
            if new_name and new_addr:
                coord = get_coordinates(new_addr)
                if coord:
                    st.session_state.place_pool[new_name] = {
                        "address": new_addr,
                        "category": new_cat,
                    }
                    st.success(f"'{new_name}'이 장소 보관함에 추가되었습니다!")
                    st.rerun()
                else:
                    st.error("주소를 지도에서 찾을 수 없습니다.")
            else:
                st.error("이름과 주소를 모두 입력해 주세요.")

    st.divider()
    st.subheader("📋 현재 등록된 장소 풀")
    for p_name, p_info in list(st.session_state.place_pool.items()):
        c1, c2 = st.columns([5, 1])
        with c1:
            style = CATEGORY_STYLE.get(p_info["category"], {"emoji": "📍"})
            st.write(
                f"{style['emoji']} **{p_name}** ({p_info['category']}) - {p_info['address']}"
            )
        with c2:
            if st.button("삭제", key=f"del_pool_{p_name}"):
                del st.session_state.place_pool[p_name]
                st.rerun()