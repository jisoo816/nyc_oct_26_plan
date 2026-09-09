import folium
from geopy.geocoders import Photon
import streamlit as st
from streamlit_folium import st_folium
from streamlit_sortables import sort_items

st.set_page_config(
    page_title="NYC Bachelorette Trip 2026",
    page_icon="🗽",
    layout="wide",
)

# -------------------------------------------------------------
# 1. 지오코더 설정 (Photon Fuzzy Search)
# -------------------------------------------------------------
geolocator = Photon(user_agent="nyc_bachelorette_planner_v7")


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
# 2. 카테고리 스타일 정의 (공항 ✈️ 추가)
# -------------------------------------------------------------
CATEGORY_STYLE = {
    "공항": {"emoji": "✈️", "bg": "#0284C7"},
    "호텔": {"emoji": "🏨", "bg": "#1E88E5"},
    "음식": {"emoji": "🍴", "bg": "#FB8C00"},
    "카페/디저트": {"emoji": "☕", "bg": "#8E24AA"},
    "콘서트/엔터": {"emoji": "🎵", "bg": "#E53935"},
    "관광/공원": {"emoji": "🌳", "bg": "#43A047"},
    "쇼핑": {"emoji": "🛍️", "bg": "#00ACC1"},
}

# -------------------------------------------------------------
# 3. 세션 상태 초기화
# -------------------------------------------------------------
if "place_pool" not in st.session_state:
    st.session_state.place_pool = {
        "Newark Liberty International Airport": {
            "address": "3 Brewster Rd, Newark, NJ 07114",
            "category": "공항",
        },
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
            "id": "row_1",
            "start_time": "10:32 AM",
            "end_time": "11:30 AM",
            "place": "Newark Liberty International Airport",
            "note": "Frontier #2282 도착 후 맨해튼 우버 이동",
        },
        {
            "id": "row_2",
            "start_time": "12:00 PM",
            "end_time": "12:30 PM",
            "place": "Thompson Central Park",
            "note": "체크인 및 짐 보관",
        },
        {
            "id": "row_3",
            "start_time": "01:30 PM",
            "end_time": "02:30 PM",
            "place": "Apollo Bagels",
            "note": "베이글 테이크아웃",
        },
        {
            "id": "row_4",
            "start_time": "07:30 PM",
            "end_time": "10:30 PM",
            "place": "Madison Square Garden",
            "note": "몬스타엑스 콘서트 관람",
        },
    ]

if "row_counter" not in st.session_state:
    st.session_state.row_counter = len(st.session_state.schedule_rows) + 1

# -------------------------------------------------------------
# 4. 탭 구성
# -------------------------------------------------------------
tab_main, tab_places = st.tabs(["🗓️ 일정표 & 동선 지도", "📍 등록된 장소 풀 관리"])

# -------------------------------------------------------------
# TAB 1: 드래그 앤 드롭 일정표 + 실시간 지도
# -------------------------------------------------------------
with tab_main:
    col_schedule, col_map = st.columns([1.35, 1.15], gap="large")

    with col_schedule:
        st.subheader("📋 일정 순서 드래그 앤 드롭")
        st.caption("👇 아래 카드들을 마우스로 위아래 끌어서 순서를 변경하세요.")

        # 고유 ID 기반 드래그 앤 드롭 리스트 생성
        items_for_sort = [
            f"{r['id']} | {r.get('start_time','')}~{r.get('end_time','')} | {r.get('place','(장소 없음)')}"
            for r in st.session_state.schedule_rows
        ]

        sorted_items = sort_items(items_for_sort, direction="vertical")

        # 드래그된 순서대로 row 재정렬
        sorted_ids = [item.split(" | ")[0] for item in sorted_items]
        id_to_row = {r["id"]: r for r in st.session_state.schedule_rows}
        st.session_state.schedule_rows = [id_to_row[rid] for rid in sorted_ids if rid in id_to_row]

        st.divider()
        st.markdown("#### ✏️ 각 행 세부 정보 입력")

        place_options = ["(장소 없음)"] + list(st.session_state.place_pool.keys())
        rows_to_delete = []

        for idx, row_data in enumerate(st.session_state.schedule_rows):
            r_id = row_data["id"]
            with st.container(border=True):
                c_num, c_start, c_end, c_place, c_del = st.columns([0.7, 1.3, 1.3, 2.7, 0.6])

                with c_num:
                    st.markdown(f"### #{idx + 1}")

                with c_start:
                    row_data["start_time"] = st.text_input(
                        "Start",
                        value=row_data.get("start_time", ""),
                        key=f"start_{r_id}",
                        placeholder="08:00 AM",
                    )

                with c_end:
                    row_data["end_time"] = st.text_input(
                        "End",
                        value=row_data.get("end_time", ""),
                        key=f"end_{r_id}",
                        placeholder="10:00 AM",
                    )

                with c_place:
                    curr_place = row_data["place"] if row_data["place"] in place_options else "(장소 없음)"
                    row_data["place"] = st.selectbox(
                        "장소 지정",
                        options=place_options,
                        index=place_options.index(curr_place),
                        key=f"place_{r_id}",
                    )

                with c_del:
                    st.write("")
                    st.write("")
                    if st.button("✖", key=f"del_{r_id}", help="행 삭제"):
                        rows_to_delete.append(idx)

                row_data["note"] = st.text_input(
                    "활동 내용 / 세부 메모",
                    value=row_data.get("note", ""),
                    key=f"note_{r_id}",
                    placeholder="상세 일정을 입력하세요",
                )

        # 삭제 대상 처리
        if rows_to_delete:
            for d_idx in sorted(rows_to_delete, reverse=True):
                st.session_state.schedule_rows.pop(d_idx)
            st.rerun()

        # 새로운 행 추가
        if st.button("➕ 새로운 일정 행 추가하기", use_container_width=True):
            st.session_state.row_counter += 1
            st.session_state.schedule_rows.append(
                {
                    "id": f"row_{st.session_state.row_counter}",
                    "start_time": "",
                    "end_time": "",
                    "place": "(장소 없음)",
                    "note": "",
                }
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
                            "category": p_info.get("category", "관광/공원"),
                            "address": p_info.get("address", ""),
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

        m = folium.Map(location=center, zoom_start=12, tiles="OpenStreetMap")

        for pt in map_points:
            style = CATEGORY_STYLE.get(
                pt["category"], {"emoji": "📍", "bg": "#333333"}
            )

            marker_html = f"""
            <div style="position: relative; display: inline-block; cursor: pointer;">
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
# TAB 2: 등록된 장소 풀 관리 (공항 카테고리 지원)
# -------------------------------------------------------------
with tab_places:
    st.subheader("📍 장소 보관함에 추가하기")

    sub_tab_search, sub_tab_manual = st.tabs(["🔍 자동 검색으로 추가", "✏️ 직접 주소 입력"])

    with sub_tab_search:
        if "search_results" not in st.session_state:
            st.session_state.search_results = []

        c_query, c_btn = st.columns([4, 1])
        with c_query:
            search_query = st.text_input(
                "장소 이름 검색",
                placeholder="예: Newark Liberty International Airport, Apollo Bagels...",
                key="place_search_input",
            )
        with c_btn:
            st.write("")
            st.write("")
            if st.button("🔍 검색", use_container_width=True):
                if search_query.strip():
                    with st.spinner("위치 찾는 중..."):
                        try:
                            results = geolocator.geocode(
                                search_query.strip(), exactly_one=False, limit=5
                            )
                            if results:
                                st.session_state.search_results = results
                            else:
                                st.warning("결과를 찾지 못했습니다. 키워드를 조금만 줄여보세요.")
                        except Exception:
                            st.error("검색 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
                else:
                    st.warning("검색할 장소 이름을 입력해 주세요.")

        if st.session_state.search_results:
            st.markdown("#### 🎯 검색 결과 선택")
            addr_options = [r.address for r in st.session_state.search_results]
            selected_address = st.selectbox("정확한 위치/주소를 선택하세요:", addr_options)

            c_name, c_cat = st.columns([2, 1])
            with c_name:
                final_name = st.text_input("일정표에 표시할 이름", value=search_query)
            with c_cat:
                final_cat = st.selectbox("카테고리 아이콘", list(CATEGORY_STYLE.keys()), key="cat_auto")

            if st.button("➕ 이 장소 보관함에 저장", type="primary", use_container_width=True):
                st.session_state.place_pool[final_name] = {
                    "address": selected_address,
                    "category": final_cat,
                }
                st.success(f"'{final_name}' 저장 완료!")
                st.session_state.search_results = []
                st.rerun()

    with sub_tab_manual:
        with st.form("manual_add_form", clear_on_submit=True):
            m_name = st.text_input("장소 이름", placeholder="예: JFK Airport")
            m_addr = st.text_input("상세 주소", placeholder="예: Queens, NY 11430")
            m_cat = st.selectbox("카테고리 아이콘", list(CATEGORY_STYLE.keys()), key="cat_manual")

            if st.form_submit_button("직접 입력으로 저장"):
                if m_name and m_addr:
                    st.session_state.place_pool[m_name] = {
                        "address": m_addr,
                        "category": m_cat,
                    }
                    st.success(f"'{m_name}' 저장 완료!")
                    st.rerun()
                else:
                    st.error("이름과 주소를 모두 입력해 주세요.")

    st.divider()
    st.subheader("📋 현재 등록된 장소 풀")
    for p_name, p_info in list(st.session_state.place_pool.items()):
        c1, c2 = st.columns([5, 1])
        with c1:
            style = CATEGORY_STYLE.get(p_info.get("category", ""), {"emoji": "📍"})
            st.write(
                f"{style['emoji']} **{p_name}** ({p_info.get('category', '')}) - {p_info.get('address', '')}"
            )
        with c2:
            if st.button("삭제", key=f"del_pool_{p_name}"):
                del st.session_state.place_pool[p_name]
                st.rerun()