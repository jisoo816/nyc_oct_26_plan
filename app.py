import folium
from geopy.geocoders import Nominatim
import pandas as pd
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
geolocator = Nominatim(user_agent="nyc_bachelorette_planner_v4")


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
# 2. 카테고리 스타일 정의 (마커 뱃지용)
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
        "time": "12:00 PM",
    },
    {
        "name": "Apollo Bagels",
        "address": "224 W 35th St, New York, NY 10001",
        "desc": "베이글 테이크아웃",
        "category": "음식",
        "time": "02:00 PM",
    },
    {
        "name": "Madison Square Garden",
        "address": "4 Pennsylvania Plaza, New York, NY 10001",
        "desc": "몬스타엑스 콘서트",
        "category": "콘서트/엔터",
        "time": "07:30 PM",
    },
]

if "custom_places" not in st.session_state:
    st.session_state.custom_places = DEFAULT_PLACES

# -------------------------------------------------------------
# 3. 메인 화면 탭 구성
# -------------------------------------------------------------
tab_schedule, tab_manage = st.tabs(
    ["🗓️ 일정 & 동선 지도", "➕ 내 장소 추가/관리"]
)

# -------------------------------------------------------------
# TAB 1: 3단 레이아웃 (드래그앤드롭 | 수정 가능한 엑셀 표 | 지도)
# -------------------------------------------------------------
with tab_schedule:
    col_order, col_table, col_map = st.columns([0.7, 1.4, 1.2], gap="medium")

    # [1열] 드래그 앤 드롭으로 장소 순서 정렬
    with col_order:
        st.markdown("#### 🔀 장소 드래그")
        st.caption("카드를 끌어서 원하는 방문 순번으로 배치하세요.")

        place_names = [p["name"] for p in st.session_state.custom_places]
        sorted_names = sort_items(place_names, direction="vertical")

        # 드래그된 순서에 맞춰 리스트 재정렬
        st.session_state.custom_places = sorted(
            st.session_state.custom_places,
            key=lambda x: (
                sorted_names.index(x["name"])
                if x["name"] in sorted_names
                else 99
            ),
        )

        st.divider()
        draw_line = st.checkbox("동선 점선 표시", value=True)

    # [2열] 자유롭게 수정 가능한 엑셀 스타일 테이블 (구분 컬럼 제거됨)
    with col_table:
        st.markdown("#### 📊 일정표 (Schedule Sheet)")
        st.caption(
            "💡 순번, 시간, 노트를 엑셀처럼 더블클릭해서 직접 수정할 수 있어요."
        )

        # 테이블 데이터 생성 (드래그 순서가 반영된 장소가 row에 순서대로 꽂힘)
        table_rows = []
        for idx, p in enumerate(st.session_state.custom_places, start=1):
            emoji = CATEGORY_STYLE.get(p.get("category", ""), {}).get(
                "emoji", "📍"
            )
            table_rows.append(
                {
                    "순번": f"#{idx}",
                    "시간": p.get("time", ""),
                    "장소 (Location)": f"{emoji} {p['name']}",
                    "노트": p.get("desc", ""),
                }
            )

        df = pd.DataFrame(table_rows)

        # 엑셀처럼 직접 셀 편집이 가능한 data_editor
        edited_df = st.data_editor(
            df,
            hide_index=True,
            use_container_width=True,
            disabled=["장소 (Location)"],  # 장소는 왼쪽 드래그로 자동 매핑
            column_config={
                "순번": st.column_config.TextColumn("순번", width="small"),
                "시간": st.column_config.TextColumn(
                    "시간", width="medium"
                ),
                "장소 (Location)": st.column_config.TextColumn(
                    "장소 (Location)", width="large"
                ),
                "노트": st.column_config.TextColumn(
                    "노트", width="large"
                ),
            },
            key="schedule_editor",
        )

        # 사용자가 표에서 직접 수정한 '시간'과 '노트'를 session_state에 즉시 동기화
        for idx, row in edited_df.iterrows():
            if idx < len(st.session_state.custom_places):
                st.session_state.custom_places[idx]["time"] = row["시간"]
                st.session_state.custom_places[idx]["desc"] = row["노트"]

        st.markdown(
            """
            > **10/6 (화):** ATL 출발(08:11 AM) ➔ EWR 도착(10:32 AM) ➔ K-타운 ➔ **08:00 PM 콘서트 (MSG)**  
            > **10/7 (수):** 조식 & 짐보관 ➔ 웨스트 빌리지 ➔ 짐 픽업 ➔ **06:30 PM 공항 이동**
            """
        )

    # [3열] 지도 렌더링
    with col_map:
        st.markdown("#### 🗺️ 동선 맵")

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

        # 뱃지 마커
        for idx, p, coord in valid_items:
            style = CATEGORY_STYLE.get(
                p.get("category", ""), {"emoji": "📍", "bg": "#333333"}
            )
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

        # 동선 경로 점선
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
# TAB 2: 새 장소 추가 및 삭제 관리
# -------------------------------------------------------------
with tab_manage:
    st.subheader("📍 새 장소 추가하기")

    with st.form("add_place_form", clear_on_submit=True):
        f_name = st.text_input(
            "장소 이름", placeholder="예: EWR Newark Liberty Airport"
        )
        f_address = st.text_input(
            "상세 주소",
            placeholder="예: 3 Brewster Rd, Newark, NJ 07114",
        )
        f_time = st.text_input("시간", placeholder="예: 10:32 AM")
        f_desc = st.text_input("노트", placeholder="예: 공항 착륙 후 맨해튼 우버 이동")
        f_cat = st.selectbox("마커 아이콘 카테고리", list(CATEGORY_STYLE.keys()))

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
                                "time": f_time,
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