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
geolocator = Nominatim(user_agent="nyc_bachelorette_planner_v6")


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
# 2. 세션 상태 초기화: Start/End 시간 지원
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
    }

if "schedule_rows" not in st.session_state:
    st.session_state.schedule_rows = [
        {
            "start_time": "12:00 PM",
            "end_time": "12:30 PM",
            "place": "Thompson Central Park",
            "note": "체크인 & 짐 보관",
        },
        {
            "start_time": "01:30 PM",
            "end_time": "02:30 PM",
            "place": "Apollo Bagels",
            "note": "베이글 픽업",
        },
        {
            "start_time": "07:30 PM",
            "end_time": "10:30 PM",
            "place": "Madison Square Garden",
            "note": "몬스타엑스 콘서트 관람",
        },
    ]

# -------------------------------------------------------------
# 3. 탭 구성
# -------------------------------------------------------------
tab_main, tab_places = st.tabs(["🗓️ 일정표 & 동선 지도", "📍 등록된 장소 풀 관리"])

# -------------------------------------------------------------
# TAB 1: 일정표 (Start/End 시간) + Pill 상단 번호 지도
# -------------------------------------------------------------
with tab_main:
    col_schedule, col_map = st.columns([1.3, 1.1], gap="large")

    with col_schedule:
        st.subheader("📋 일정표 편집")
        st.caption("Start/End 시간, 장소를 자유롭게 설정해 동선을 완성하세요.")

        place_options = ["(장소 없음)"] + list(st.session_state.place_pool.keys())

        # 행 렌더링
        for idx, row_data in enumerate(st.session_state.schedule_rows):
            with st.container(border=True):
                # 1열: 순번, 2열: 시작시간, 3열: 종료시간, 4열: 장소지정, 5~7열: 이동/삭제
                c_num, c_start, c_end, c_place, c_up, c_down, c_del = st.columns(
                    [0.7, 1.2, 1.2, 2.5, 0.5, 0.5, 0.5]
                )

                with c_num:
                    st.markdown(f"### #{idx + 1}")

                with c_start:
                    new_start = st.text_input(
                        "Start",
                        value=row_data.get("start_time", ""),
                        key=f"start_{idx}",
                        placeholder="08:00 AM",
                    )
                    st.session_state.schedule_rows[idx]["start_time"] = new_start

                with c_end:
                    new_end = st.text_input(
                        "End",
                        value=row_data.get("end_time", ""),
                        key=f"end_{idx}",
                        placeholder="10:00 AM",
                    )
                    st.session_state.schedule_rows[idx]["end_time"] = new_end

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
                    "활동 내용 / 세부 노트",
                    value=row_data.get("note", ""),
                    key=f"note_{idx}",
                    placeholder="식사 메뉴, 이동 팁 등",
                )
                st.session_state.schedule_rows[idx]["note"] = new_note

        # 행 추가 버튼
        if st.button("➕ 새로운 일정 행 추가하기", use_container_width=True):
            st.session_state.schedule_rows.append(
                {"start_time": "", "end_time": "", "place": "(장소 없음)", "note": ""}
            )
            st.rerun()

        st.divider()
        draw_line = st.checkbox("지도에 동선 점선 연결하기", value=True)

    # 우측 지도
    with col_map:
        st.subheader("🗺️ 실시간 동선 맵")

        coords_list = []
        map_points = []

        for idx, row in enumerate(st.session_state.schedule_rows, start=1):
            p_name = row["place"]
            if p_name != "(장소 없음)" and p_name in st.session_state.place_pool:
                p_info = st.session_state.place_pool[p_name]
                coord = get_coordinates(p_info["address"])
                if coord:
                    coords_list.append(coord)
                    time_display = f"{row.get('start_time', '')} ~ {row.get('end_time', '')}".strip(" ~")
                    map_points.append(
                        {
                            "seq": idx,
                            "name": p_name,
                            "time_str": time_display if time_display else "시간 미정",
                            "note": row.get("note", ""),
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

            # Pill(알약) 상단에 순서 넘버 배지가 떠 있는 디자인
            marker_html = f"""
            <div style="position: relative; display: inline-block; cursor: pointer;">
                <!-- 1. 상단 순서 넘버 배지 -->
                <div style="
                    position: absolute;
                    top: -12px;
                    left: 50%;
                    transform: translateX(-50%);
                    background-color: #111827;
                    color: #FFFFFF;
                    border: 1.5px solid #FFFFFF;
                    border-radius: 10px;
                    padding: 1px 6px;
                    font-size: 11px;
                    font-weight: 800;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    z-index: 10;
                    white-space: nowrap;
                ">
                    #{pt['seq']}
                </div>

                <!-- 2. 메인 Pill (아이콘 + 장소명) -->
                <div style="
                    background-color: {style['bg']};
                    color: white;
                    border: 2px solid #FFFFFF;
                    border-radius: 20px;
                    padding: 4px 10px;
                    font-size: 12px;
                    font-weight: 600;
                    display: flex;
                    align-items: center;
                    gap: 5px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
                    white-space: nowrap;
                ">
                    <span style="font-size: 14px;">{style['emoji']}</span>
                    <span>{pt['name']}</span>
                </div>
            </div>
            """

            popup_html = f"""
            <div style="font-family: sans-serif; font-size: 13px; line-height: 1.4;">
                <b style="font-size: 14px; color: #111;">#{pt['seq']} {pt['name']}</b><br>
                <span style="color: #666;">⏰ {pt['time_str']}</span><br>
                <span style="color: #444;">📍 {pt['address']}</span><br>
                <hr style="margin: 6px 0; border: none; border-top: 1px solid #eee;">
                <b>메모:</b> {pt['note']}
            </div>
            """

            folium.Marker(
                location=pt["coord"],
                tooltip=f"#{pt['seq']} {pt['name']} ({pt['time_str']})",
                popup=folium.Popup(popup_html, max_width=260),
                icon=folium.DivIcon(
                    html=marker_html,
                    icon_size=(140, 40),
                    icon_anchor=(70, 20),
                ),
            ).add_to(m)

        if draw_line and len(coords_list) > 1:
            folium.PolyLine(
                locations=coords_list,
                color="#0066cc",
                weight=3,
                opacity=0.85,
                dash_array="6, 6",
            ).add_to(m)

        st_folium(m, width="100%", height=620)

# -------------------------------------------------------------
# TAB 2: 장소 보관함(풀) 추가 및 관리
# -------------------------------------------------------------
# -------------------------------------------------------------
# TAB 2: 장소 보관함(풀) 추가 및 관리 (자동 검색 지원)
# -------------------------------------------------------------
with tab_places:
    st.subheader("📍 이름으로 장소 검색 & 보관함에 추가")
    st.caption("장소 이름(상호명)만 입력하고 검색하면 주소를 자동으로 찾아줘요.")

    if "search_results" not in st.session_state:
        st.session_state.search_results = []

    # 1. 검색어 입력 및 자동 검색
    c_query, c_btn = st.columns([4, 1])
    with c_query:
        search_query = st.text_input(
            "장소 이름 검색",
            placeholder="예: L'Industrie Pizzeria, Buvette, Kat'z Deli...",
            key="place_search_input"
        )
    with c_btn:
        st.write("")
        st.write("")
        if st.button("🔍 주소 검색", use_container_width=True):
            if search_query.strip():
                with st.spinner("주소 찾는 중..."):
                    # 뉴욕 내 장소 우선 검색
                    query = f"{search_query}, New York"
                    try:
                        results = geolocator.geocode(query, exactly_one=False, limit=5)
                        if results:
                            st.session_state.search_results = results
                        else:
                            st.warning("결과를 찾지 못했습니다. 상호명을 조금 더 구체적으로 입력해 보세요.")
                    except Exception as e:
                        st.error("검색 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
            else:
                st.warning("검색할 장소 이름을 입력해 주세요.")

    # 2. 검색 결과 드롭다운 선택 후 최종 등록
    if st.session_state.search_results:
        st.markdown("#### 🎯 검색 결과 선택")
        addr_options = [r.address for r in st.session_state.search_results]
        selected_address = st.selectbox("정확한 위치/주소를 선택하세요:", addr_options)
        
        c_name, c_cat = st.columns([2, 1])
        with c_name:
            final_name = st.text_input("일정표에 표시할 이름", value=search_query)
        with c_cat:
            final_cat = st.selectbox("카테고리 아이콘", list(CATEGORY_STYLE.keys()))

        if st.button("➕ 이 장소 보관함에 저장", type="primary", use_container_width=True):
            # 선택한 주소의 위경도 찾기
            selected_loc = next(r for r in st.session_state.search_results if r.address == selected_address)
            st.session_state.place_pool[final_name] = {
                "address": selected_address,
                "category": final_cat
            }
            st.success(f"'{final_name}'이(가) 장소 보관함에 추가되었습니다!")
            st.session_state.search_results = []  # 검색 결과 초기화
            st.rerun()

    st.divider()
    st.subheader("📋 현재 등록된 장소 풀")
    for p_name, p_info in list(st.session_state.place_pool.items()):
        c1, c2 = st.columns([5, 1])
        with c1:
            style = CATEGORY_STYLE.get(p_info.get("category", ""), {"emoji": "📍"})
            st.write(f"{style['emoji']} **{p_name}** ({p_info.get('category', '')}) - {p_info.get('address', '')}")
        with c2:
            if st.button("삭제", key=f"del_pool_{p_name}"):
                del st.session_state.place_pool[p_name]
                st.rerun()