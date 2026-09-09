import folium
from geopy.geocoders import Photon
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="NYC Bachelorette Trip 2026",
    page_icon="🗽",
    layout="wide",
)

# -------------------------------------------------------------
# 0. 커스텀 CSS (여백 및 테이블 스타일)
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.8rem; padding-bottom: 2rem; }
    div[data-testid="stTextInput"] label, div[data-testid="stSelectbox"] label {
        display: none !important;
    }
    div[data-testid="stTextInput"], div[data-testid="stSelectbox"] {
        margin-bottom: 0px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 10px 14px !important;
        margin-bottom: 10px !important;
        border-radius: 12px !important;
        background: #181c24 !important;
        border: 1px solid #2a313d !important;
    }
    div[data-testid="stButton"] button {
        padding: 2px 8px !important;
        height: 36px !important;
        min-height: 36px !important;
        border-radius: 8px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 1. 지오코더 설정 (Photon Fuzzy Search)
# -------------------------------------------------------------
geolocator = Photon(user_agent="nyc_bachelorette_planner_v10")


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
    "공항": {"emoji": "✈️", "bg": "#0284C7", "border": "#38bdf8"},
    "호텔": {"emoji": "🏨", "bg": "#2563EB", "border": "#60a5fa"},
    "음식": {"emoji": "🍴", "bg": "#EA580C", "border": "#fb923c"},
    "카페/디저트": {"emoji": "☕", "bg": "#9333EA", "border": "#c084fc"},
    "콘서트/엔터": {"emoji": "🎵", "bg": "#DC2626", "border": "#f87171"},
    "관광/공원": {"emoji": "🌳", "bg": "#16A34A", "border": "#4ade80"},
    "쇼핑": {"emoji": "🛍️", "bg": "#0891B2", "border": "#22d3ee"},
}

# -------------------------------------------------------------
# 2. 세션 상태 초기화
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
        "Buvette": {
            "address": "42 Grove St, New York, NY 10014",
            "category": "음식",
        },
    }

if "days_data" not in st.session_state:
    st.session_state.days_data = {
        "10/6 (화)": [
            {
                "id": "row_106_1",
                "start_time": "10:32 AM",
                "end_time": "11:30 AM",
                "place": "Newark Liberty International Airport",
                "note": "Frontier #2282 도착 후 맨해튼 우버 이동",
            },
            {
                "id": "row_106_2",
                "start_time": "12:00 PM",
                "end_time": "12:30 PM",
                "place": "Thompson Central Park",
                "note": "체크인 및 짐 보관",
            },
            {
                "id": "row_106_3",
                "start_time": "01:30 PM",
                "end_time": "02:30 PM",
                "place": "Apollo Bagels",
                "note": "베이글 테이크아웃",
            },
            {
                "id": "row_106_4",
                "start_time": "07:30 PM",
                "end_time": "10:30 PM",
                "place": "Madison Square Garden",
                "note": "몬스타엑스 콘서트 관람",
            },
        ],
        "10/7 (수)": [
            {
                "id": "row_107_1",
                "start_time": "08:30 AM",
                "end_time": "09:30 AM",
                "place": "Thompson Central Park",
                "note": "체크아웃 & 호텔 짐 보관",
            },
            {
                "id": "row_107_2",
                "start_time": "11:30 AM",
                "end_time": "01:30 PM",
                "place": "Buvette",
                "note": "웨스트 빌리지 브런치",
            },
            {
                "id": "row_107_3",
                "start_time": "05:45 PM",
                "end_time": "06:15 PM",
                "place": "Thompson Central Park",
                "note": "호텔 짐 픽업 후 공항 출발",
            },
        ],
    }

if "current_day" not in st.session_state:
    st.session_state.current_day = list(st.session_state.days_data.keys())[0]

if "row_counter" not in st.session_state:
    st.session_state.row_counter = 100

# -------------------------------------------------------------
# 3. 탭 구성
# -------------------------------------------------------------
tab_main, tab_places = st.tabs(["🗓️ 일정표 & 동선 지도", "📍 등록된 장소 풀 관리"])

# -------------------------------------------------------------
# TAB 1: 좌측 편집 카드 + 우측 [상단 엑셀 요약표 | 하단 동선 맵]
# -------------------------------------------------------------
with tab_main:
    col_schedule, col_map = st.columns([1.15, 1.25], gap="large")

    # 좌측 편집 카드 목록
    with col_schedule:
        c_day_select, c_day_add = st.columns([3, 1.1])
        with c_day_select:
            day_list = list(st.session_state.days_data.keys())
            curr_idx = (
                day_list.index(st.session_state.current_day)
                if st.session_state.current_day in day_list
                else 0
            )
            selected_day = st.radio(
                "날짜 선택",
                options=day_list,
                index=curr_idx,
                horizontal=True,
                label_visibility="collapsed",
            )
            st.session_state.current_day = selected_day

        with c_day_add:
            with st.popover("➕ 날짜 추가"):
                new_date_label = st.text_input(
                    "새 날짜 명칭", placeholder="예: 10/8 (목)"
                )
                if st.button("날짜 생성", use_container_width=True):
                    if (
                        new_date_label.strip()
                        and new_date_label not in st.session_state.days_data
                    ):
                        st.session_state.days_data[new_date_label.strip()] = []
                        st.session_state.current_day = new_date_label.strip()
                        st.rerun()

        active_rows = st.session_state.days_data[st.session_state.current_day]
        place_options = ["(장소 없음)"] + list(
            st.session_state.place_pool.keys()
        )

        move_up_idx = None
        move_down_idx = None
        delete_idx = None

        for idx, row in enumerate(active_rows):
            r_id = row["id"]
            curr_place = (
                row["place"]
                if row["place"] in place_options
                else "(장소 없음)"
            )
            p_cat = st.session_state.place_pool.get(curr_place, {}).get(
                "category", ""
            )
            cat_style = CATEGORY_STYLE.get(
                p_cat, {"emoji": "📍", "bg": "#334155", "border": "#64748b"}
            )

            with st.container(border=True):
                c_header, c_btns = st.columns([4, 1.3])
                with c_header:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                            <span style="background: #111827; color: #fff; border-radius: 6px; padding: 2px 8px; font-weight: 800; font-size: 13px;">#{idx + 1}</span>
                            <span style="background: {cat_style['bg']}; color: #ffffff; border-radius: 6px; padding: 2px 10px; font-weight: 700; font-size: 13px; border: 1px solid {cat_style['border']};">
                                {cat_style['emoji']} {curr_place}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_btns:
                    b_up, b_down, b_del = st.columns([1, 1, 1])
                    with b_up:
                        if st.button(
                            "▲",
                            key=f"up_{r_id}",
                            disabled=(idx == 0),
                            help="위로 올리기",
                        ):
                            move_up_idx = idx
                    with b_down:
                        if st.button(
                            "▼",
                            key=f"down_{r_id}",
                            disabled=(idx == len(active_rows) - 1),
                            help="아래로 내리기",
                        ):
                            move_down_idx = idx
                    with b_del:
                        if st.button("✖", key=f"del_{r_id}", help="삭제"):
                            delete_idx = idx

                c_start, c_tilde, c_end, c_select = st.columns(
                    [1.1, 0.2, 1.1, 2.5]
                )
                with c_start:
                    row["start_time"] = st.text_input(
                        "Start",
                        value=row.get("start_time", ""),
                        key=f"start_{r_id}",
                        placeholder="Start",
                    )
                with c_tilde:
                    st.markdown(
                        "<div style='text-align: center; line-height: 38px; color: #64748b;'>~</div>",
                        unsafe_allow_html=True,
                    )
                with c_end:
                    row["end_time"] = st.text_input(
                        "End",
                        value=row.get("end_time", ""),
                        key=f"end_{r_id}",
                        placeholder="End",
                    )
                with c_select:
                    row["place"] = st.selectbox(
                        "장소 변경",
                        options=place_options,
                        index=place_options.index(curr_place),
                        key=f"place_{r_id}",
                    )

                row["note"] = st.text_input(
                    "메모",
                    value=row.get("note", ""),
                    key=f"note_{r_id}",
                    placeholder="활동 내용이나 팁을 입력하세요",
                )

        if move_up_idx is not None:
            (
                active_rows[move_up_idx - 1],
                active_rows[move_up_idx],
            ) = (
                active_rows[move_up_idx],
                active_rows[move_up_idx - 1],
            )
            st.rerun()

        if move_down_idx is not None:
            (
                active_rows[move_down_idx + 1],
                active_rows[move_down_idx],
            ) = (
                active_rows[move_down_idx],
                active_rows[move_down_idx + 1],
            )
            st.rerun()

        if delete_idx is not None:
            active_rows.pop(delete_idx)
            st.rerun()

        if st.button("➕ 새로운 일정 카드 추가", use_container_width=True):
            st.session_state.row_counter += 1
            active_rows.append(
                {
                    "id": f"row_{st.session_state.row_counter}",
                    "start_time": "",
                    "end_time": "",
                    "place": "(장소 없음)",
                    "note": "",
                }
            )
            st.rerun()

    # 우측: [1] 엑셀 스타일 요약 테이블 + [2] 동선 지도
    with col_map:
        active_rows = st.session_state.days_data[st.session_state.current_day]

        # ---------------- 엑셀 스타일 요약 테이블 ----------------
        st.markdown(f"#### 📊 {st.session_state.current_day} 일정 요약표")

        table_data = []
        for idx, r in enumerate(active_rows, start=1):
            p_name = r.get("place", "(장소 없음)")
            p_cat = st.session_state.place_pool.get(p_name, {}).get("category", "")
            emoji = CATEGORY_STYLE.get(p_cat, {}).get("emoji", "📍")
            
            s_time = r.get("start_time", "").strip()
            e_time = r.get("end_time", "").strip()
            time_display = f"{s_time} ~ {e_time}".strip(" ~") if (s_time or e_time) else "-"

            table_data.append(
                {
                    "순번": f"#{idx}",
                    "시간": time_display,
                    "장소": f"{emoji} {p_name}" if p_name != "(장소 없음)" else "-",
                    "내용 / 노트": r.get("note", "") or "-",
                }
            )

        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "순번": st.column_config.TextColumn("순번", width="small"),
                "시간": st.column_config.TextColumn("시간", width="medium"),
                "장소": st.column_config.TextColumn("장소", width="medium"),
                "내용 / 노트": st.column_config.TextColumn("내용 / 노트", width="large"),
            },
        )

        st.divider()

        # ---------------- 지도 렌더링 ----------------
        st.markdown(f"#### 🗺️ {st.session_state.current_day} 동선 맵")
        draw_line = st.checkbox("지도에 경로 점선 연결하기", value=True)

        coords_list = []
        map_points = []

        for idx, row in enumerate(active_rows, start=1):
            p_name = row["place"]
            if p_name != "(장소 없음)" and p_name in st.session_state.place_pool:
                p_info = st.session_state.place_pool[p_name]
                coord = get_coordinates(p_info["address"])
                if coord:
                    coords_list.append(coord)
                    time_display = (
                        f"{row.get('start_time', '')} ~ {row.get('end_time', '')}".strip(
                            " ~"
                        )
                    )
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

        st_folium(m, width="100%", height=520)

# -------------------------------------------------------------
# TAB 2: 등록된 장소 풀 관리
# -------------------------------------------------------------
with tab_places:
    st.subheader("📍 장소 보관함에 추가하기")

    sub_tab_search, sub_tab_manual = st.tabs(
        ["🔍 자동 검색으로 추가", "✏️ 직접 주소 입력"]
    )

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
                                search_query.strip(),
                                exactly_one=False,
                                limit=5,
                            )
                            if results:
                                st.session_state.search_results = results
                            else:
                                st.warning(
                                    "결과를 찾지 못했습니다. 키워드를 조금만 줄여보세요."
                                )
                        except Exception:
                            st.error(
                                "검색 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
                            )
                else:
                    st.warning("검색할 장소 이름을 입력해 주세요.")

        if st.session_state.search_results:
            st.markdown("#### 🎯 검색 결과 선택")
            addr_options = [r.address for r in st.session_state.search_results]
            selected_address = st.selectbox(
                "정확한 위치/주소를 선택하세요:", addr_options
            )

            c_name, c_cat = st.columns([2, 1])
            with c_name:
                final_name = st.text_input(
                    "일정표에 표시할 이름", value=search_query
                )
            with c_cat:
                final_cat = st.selectbox(
                    "카테고리 아이콘",
                    list(CATEGORY_STYLE.keys()),
                    key="cat_auto",
                )

            if st.button(
                "➕ 이 장소 보관함에 저장",
                type="primary",
                use_container_width=True,
            ):
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
            m_addr = st.text_input(
                "상세 주소", placeholder="예: Queens, NY 11430"
            )
            m_cat = st.selectbox(
                "카테고리 아이콘", list(CATEGORY_STYLE.keys()), key="cat_manual"
            )

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
            style = CATEGORY_STYLE.get(
                p_info.get("category", ""), {"emoji": "📍"}
            )
            st.write(
                f"{style['emoji']} **{p_name}** ({p_info.get('category', '')}) - {p_info.get('address', '')}"
            )
        with c2:
            if st.button("삭제", key=f"del_pool_{p_name}"):
                del st.session_state.place_pool[p_name]
                st.rerun()