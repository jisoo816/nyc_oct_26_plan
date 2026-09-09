import folium
from geopy.geocoders import Photon
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="NYC 2026",
    page_icon="🗽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------
# 0. 모바일 CSS (화면 밖 짤림 방지 및 터치 최적화)
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container { 
        padding-top: 4.2rem !important; 
        padding-bottom: 2.5rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    
    button[data-baseweb="tab"] {
        font-size: 13px !important;
        font-weight: 700 !important;
        padding: 6px 8px !important;
    }

    /* 입력창 라벨 숨김 및 여백 */
    div[data-testid="stTextInput"] label, div[data-testid="stSelectbox"] label, div[data-testid="stCheckbox"] label {
        display: none !important;
    }
    div[data-testid="stTextInput"], div[data-testid="stSelectbox"], div[data-testid="stCheckbox"] {
        margin-bottom: 4px !important;
    }
    
    /* 모바일 카드 박스 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 10px 8px !important;
        margin-bottom: 12px !important;
        border-radius: 12px !important;
        background: #181c24 !important;
        border: 1px solid #2a313d !important;
    }

    /* ★ Streamlit 모바일 컬럼 세로 꺾임 강제 무력화 ★ */
    @media (max-width: 640px), (max-width: 768px) {
        div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            gap: 4px !important;
            width: 100% !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stColumn"] {
            width: auto !important;
            flex: 1 1 0px !important;
            min-width: 0 !important;
        }
    }

    /* 버튼 컴팩트 스타일 */
    div[data-testid="stButton"] button {
        padding: 0px !important;
        height: 36px !important;
        min-height: 36px !important;
        font-size: 13px !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 1. 지오코더 설정 (Photon)
# -------------------------------------------------------------
geolocator = Photon(user_agent="nyc_bachelorette_mobile_v6")


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
    "공항": {"emoji": "✈️", "bg": "#0284C7"},
    "호텔": {"emoji": "🏨", "bg": "#2563EB"},
    "음식": {"emoji": "🍴", "bg": "#EA580C"},
    "카페/디저트": {"emoji": "☕", "bg": "#9333EA"},
    "콘서트/엔터": {"emoji": "🎵", "bg": "#DC2626"},
    "관광/공원": {"emoji": "🌳", "bg": "#16A34A"},
    "쇼핑": {"emoji": "🛍️", "bg": "#0891B2"},
}

# -------------------------------------------------------------
# 2. 세션 상태 초기화
# -------------------------------------------------------------
if "place_pool" not in st.session_state:
    st.session_state.place_pool = {
        "ATL 공항": {
            "address": "6000 N Terminal Pkwy, Atlanta, GA 30320",
            "category": "공항",
        },
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
                "id": "row_106_0",
                "start_time": "08:11 AM",
                "end_time": "10:32 AM",
                "place": "ATL 공항",
                "note": "Frontier #2282 탑승 (ATL → EWR)",
                "show_on_map": False,
            },
            {
                "id": "row_106_1",
                "start_time": "10:32 AM",
                "end_time": "11:30 AM",
                "place": "Newark Liberty International Airport",
                "note": "도착 후 맨해튼 우버 이동",
                "show_on_map": True,
            },
            {
                "id": "row_106_2",
                "start_time": "12:00 PM",
                "end_time": "12:30 PM",
                "place": "Thompson Central Park",
                "note": "체크인 및 짐 보관",
                "show_on_map": True,
            },
            {
                "id": "row_106_3",
                "start_time": "01:30 PM",
                "end_time": "02:30 PM",
                "place": "Apollo Bagels",
                "note": "베이글 테이크아웃",
                "show_on_map": True,
            },
            {
                "id": "row_106_4",
                "start_time": "07:30 PM",
                "end_time": "10:30 PM",
                "place": "Madison Square Garden",
                "note": "몬스타엑스 콘서트 관람",
                "show_on_map": True,
            },
        ],
        "10/7 (수)": [
            {
                "id": "row_107_1",
                "start_time": "08:30 AM",
                "end_time": "09:30 AM",
                "place": "Thompson Central Park",
                "note": "체크아웃 & 호텔 짐 보관",
                "show_on_map": True,
            },
            {
                "id": "row_107_2",
                "start_time": "11:30 AM",
                "end_time": "01:30 PM",
                "place": "Buvette",
                "note": "웨스트 빌리지 브런치",
                "show_on_map": True,
            },
            {
                "id": "row_107_3",
                "start_time": "05:45 PM",
                "end_time": "06:15 PM",
                "place": "Thompson Central Park",
                "note": "호텔 짐 픽업 후 공항 출발",
                "show_on_map": True,
            },
        ],
    }

if "current_day" not in st.session_state:
    st.session_state.current_day = list(st.session_state.days_data.keys())[0]

if "row_counter" not in st.session_state:
    st.session_state.row_counter = 100

# -------------------------------------------------------------
# 3. 날짜 선택
# -------------------------------------------------------------
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
)
st.session_state.current_day = selected_day

# -------------------------------------------------------------
# 4. 상단 탭 구성
# -------------------------------------------------------------
tab_view, tab_edit, tab_places = st.tabs(
    ["🗓️ 일정표 & 지도", "✏️ 일정 카드 편집", "📍 장소 보관함"]
)

active_rows = st.session_state.days_data[st.session_state.current_day]
place_options = ["(장소 없음)"] + list(st.session_state.place_pool.keys())

# =============================================================
# TAB 1: 🗓️ 일정표 & 동선 지도 (조회)
# =============================================================
with tab_view:
    st.markdown(f"#### 📊 {st.session_state.current_day} 타임라인")
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
                "내용 / 메모": r.get("note", "") or "-",
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
            "내용 / 메모": st.column_config.TextColumn("메모", width="large"),
        },
    )

    st.divider()
    st.markdown(f"#### 🗺️ {st.session_state.current_day} 동선 맵")
    draw_line = st.checkbox("경로 점선 연결", value=True)

    coords_list = []
    map_points = []
    map_seq = 1

    for idx, row in enumerate(active_rows, start=1):
        if not row.get("show_on_map", True):
            continue
        p_name = row["place"]
        if p_name != "(장소 없음)" and p_name in st.session_state.place_pool:
            p_info = st.session_state.place_pool[p_name]
            coord = get_coordinates(p_info["address"])
            if coord:
                coords_list.append(coord)
                time_display = f"{row.get('start_time', '')} ~ {row.get('end_time', '')}".strip(" ~")
                map_points.append(
                    {
                        "seq": map_seq,
                        "name": p_name,
                        "time_str": time_display if time_display else "시간 미정",
                        "note": row.get("note", ""),
                        "category": p_info.get("category", "관광/공원"),
                        "address": p_info.get("address", ""),
                        "coord": coord,
                    }
                )
                map_seq += 1

    center = (
        [sum(c[0] for c in coords_list) / len(coords_list), sum(c[1] for c in coords_list) / len(coords_list)]
        if coords_list
        else [40.7580, -73.9855]
    )

    m = folium.Map(location=center, zoom_start=12, tiles="OpenStreetMap")

    for pt in map_points:
        style = CATEGORY_STYLE.get(pt["category"], {"emoji": "📍", "bg": "#333333"})
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
                z-index: 10;
                white-space: nowrap;
            ">
                #{pt['seq']}
            </div>
            <div style="
                background-color: {style['bg']};
                color: white;
                border: 2px solid #FFFFFF;
                border-radius: 18px;
                padding: 4px 9px;
                font-size: 12px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 4px;
                white-space: nowrap;
            ">
                <span>{style['emoji']}</span>
                <span>#{pt['seq']} {pt['name']}</span>
            </div>
        </div>
        """
        popup_html = f"""
        <b>#{pt['seq']} {pt['name']}</b><br>
        ⏰ {pt['time_str']}<br>
        📍 {pt['address']}<br>
        <hr style="margin: 4px 0;">{pt['note']}
        """
        folium.Marker(
            location=pt["coord"],
            tooltip=f"#{pt['seq']} {pt['name']}",
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.DivIcon(html=marker_html, icon_size=(130, 36), icon_anchor=(65, 18)),
        ).add_to(m)

    if draw_line and len(coords_list) > 1:
        folium.PolyLine(locations=coords_list, color="#0066cc", weight=3, opacity=0.85, dash_array="6, 6").add_to(m)

    st_folium(m, width="100%", height=500)

# =============================================================
# TAB 2: ✏️ 일정 카드 편집 (모바일 3단계 레이아웃)
# =============================================================
with tab_edit:
    st.caption("카드를 수정하거나 순서를 변경하세요.")

    move_up_idx = None
    move_down_idx = None
    delete_idx = None
    insert_below_idx = None

    for idx, row in enumerate(active_rows):
        r_id = row["id"]
        curr_place = row["place"] if row["place"] in place_options else "(장소 없음)"

        if "show_on_map" not in row:
            row["show_on_map"] = True

        with st.container(border=True):
            # [1단 컨트롤 바] #순번 | 지도 🗺️ | ▲ | ▼ | +↓ | ✖ (안 잘리도록 균등 6분할)
            c_num, c_map, c_u, c_d, c_in, c_x = st.columns([1.1, 1.3, 1.0, 1.0, 1.0, 1.0])
            with c_num:
                st.markdown(
                    f"<div style='line-height:36px; font-weight:800; font-size:16px;'>#{idx + 1}</div>",
                    unsafe_allow_html=True,
                )
            with c_map:
                st.write("")
                row["show_on_map"] = st.checkbox("🗺️", value=row["show_on_map"], key=f"map_{r_id}", help="지도 표시 여부")
            with c_u:
                if st.button("▲", key=f"u_{r_id}", disabled=(idx == 0), help="위로"):
                    move_up_idx = idx
            with c_d:
                if st.button("▼", key=f"d_{r_id}", disabled=(idx == len(active_rows) - 1), help="아래로"):
                    move_down_idx = idx
            with c_in:
                if st.button("+↓", key=f"in_{r_id}", help="아래에 새 일정 추가"):
                    insert_below_idx = idx
            with c_x:
                if st.button("✖", key=f"x_{r_id}", help="삭제"):
                    delete_idx = idx

            # [2단 시간 입력] Start 시간과 End 시간을 확실하게 2칸으로 분할
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                row["start_time"] = st.text_input(
                    "시작",
                    value=row.get("start_time", ""),
                    key=f"start_{r_id}",
                    placeholder="시작 (예: 08:00 AM)",
                )
            with t_col2:
                row["end_time"] = st.text_input(
                    "종료",
                    value=row.get("end_time", ""),
                    key=f"end_{r_id}",
                    placeholder="종료 (예: 10:30 AM)",
                )

            # [3단 장소 선택]
            row["place"] = st.selectbox(
                "장소",
                options=place_options,
                index=place_options.index(curr_place),
                key=f"place_{r_id}",
            )

            # [4단 메모 입력]
            row["note"] = st.text_input(
                "메모",
                value=row.get("note", ""),
                key=f"note_{r_id}",
                placeholder="활동 내용이나 팁을 입력하세요",
            )

    # 액션 반영
    if insert_below_idx is not None:
        st.session_state.row_counter += 1
        active_rows.insert(
            insert_below_idx + 1,
            {"id": f"row_{st.session_state.row_counter}", "start_time": "", "end_time": "", "place": "(장소 없음)", "note": "", "show_on_map": True},
        )
        st.rerun()

    if move_up_idx is not None:
        active_rows[move_up_idx - 1], active_rows[move_up_idx] = active_rows[move_up_idx], active_rows[move_up_idx - 1]
        st.rerun()

    if move_down_idx is not None:
        active_rows[move_down_idx + 1], active_rows[move_down_idx] = active_rows[move_down_idx], active_rows[move_down_idx + 1]
        st.rerun()

    if delete_idx is not None:
        active_rows.pop(delete_idx)
        st.rerun()

    if st.button("➕ 맨 아래에 새 일정 추가", use_container_width=True):
        st.session_state.row_counter += 1
        active_rows.append(
            {"id": f"row_{st.session_state.row_counter}", "start_time": "", "end_time": "", "place": "(장소 없음)", "note": "", "show_on_map": True}
        )
        st.rerun()

# =============================================================
# TAB 3: 📍 장소 보관함 관리
# =============================================================
with tab_places:
    st.subheader("📍 장소 보관함 관리")

    sub_search, sub_manual = st.tabs(["🔍 자동 검색 추가", "✏️ 직접 입력 추가"])

    with sub_search:
        if "search_results" not in st.session_state:
            st.session_state.search_results = []

        search_query = st.text_input("장소 이름", placeholder="예: Apollo Bagels, Buvette...", key="p_search")
        if st.button("🔍 주소 검색", use_container_width=True):
            if search_query.strip():
                with st.spinner("검색 중..."):
                    try:
                        results = geolocator.geocode(search_query.strip(), exactly_one=False, limit=5)
                        st.session_state.search_results = results if results else []
                        if not results:
                            st.warning("결과를 찾지 못했습니다.")
                    except Exception:
                        st.error("검색 오류가 발생했습니다.")

        if st.session_state.search_results:
            addr_options = [r.address for r in st.session_state.search_results]
            selected_addr = st.selectbox("주소 선택", addr_options)
            final_name = st.text_input("표시 이름", value=search_query)
            final_cat = st.selectbox("카테고리", list(CATEGORY_STYLE.keys()), key="cat_s")

            if st.button("➕ 보관함에 저장", type="primary", use_container_width=True):
                st.session_state.place_pool[final_name] = {"address": selected_addr, "category": final_cat}
                st.success(f"'{final_name}' 저장 완료!")
                st.session_state.search_results = []
                st.rerun()

    with sub_manual:
        with st.form("manual_form", clear_on_submit=True):
            m_name = st.text_input("장소 이름")
            m_addr = st.text_input("상세 주소")
            m_cat = st.selectbox("카테고리", list(CATEGORY_STYLE.keys()), key="cat_m")
            if st.form_submit_button("직접 저장", use_container_width=True):
                if m_name and m_addr:
                    st.session_state.place_pool[m_name] = {"address": m_addr, "category": m_cat}
                    st.success("저장 완료!")
                    st.rerun()

    st.divider()
    st.markdown("#### 📋 등록된 장소 목록")
    for p_name, p_info in list(st.session_state.place_pool.items()):
        c1, c2, c3 = st.columns([3.5, 1, 1])
        with c1:
            style = CATEGORY_STYLE.get(p_info.get("category", ""), {"emoji": "📍"})
            st.write(f"{style['emoji']} **{p_name}**")
        with c2:
            with st.popover("✏️"):
                e_name = st.text_input("이름", value=p_name, key=f"en_{p_name}")
                e_addr = st.text_input("주소", value=p_info.get("address", ""), key=f"ea_{p_name}")
                e_cat = st.selectbox(
                    "카테고리",
                    list(CATEGORY_STYLE.keys()),
                    index=list(CATEGORY_STYLE.keys()).index(p_info.get("category", "관광/공원")),
                    key=f"ec_{p_name}",
                )
                if st.button("저장", key=f"sv_{p_name}", use_container_width=True):
                    if e_name != p_name:
                        del st.session_state.place_pool[p_name]
                        for d in st.session_state.days_data.values():
                            for r in d:
                                if r.get("place") == p_name:
                                    r["place"] = e_name
                    st.session_state.place_pool[e_name] = {"address": e_addr, "category": e_cat}
                    st.rerun()
        with c3:
            if st.button("✖ 삭제", key=f"dp_{p_name}"):
                del st.session_state.place_pool[p_name]
                st.rerun()