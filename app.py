import folium
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="NYC Bachelorette Trip 2026",
    page_icon="🗽",
    layout="wide",
)

st.title("🗽 NYC Bachelorette Trip (10/6 - 10/7)")

# -------------------------------------------------------------
# 1. 장소 데이터 (위도, 경도, 설명)
# -------------------------------------------------------------
LOCATIONS = {
    "호텔 (Thompson Central Park)": {
        "coord": [40.7648, -73.9787],
        "desc": "숙소 / 짐 보관 (119 W 56th St)",
        "icon": "bed",
    },
    "점심 (K-타운 한식)": {
        "coord": [40.7477, -73.9868],
        "desc": "피로 회복 한식 (32nd St K-Town)",
        "icon": "cutlery",
    },
    "센트럴 파크": {
        "coord": [40.7685, -73.9742],
        "desc": "호텔 앞 산책 & 사진 타임",
        "icon": "tree-conifer",
    },
    "콘서트장 (Madison Square Garden)": {
        "coord": [40.7505, -73.9934],
        "desc": "몬스타엑스 콘서트 (8:00 PM)",
        "icon": "music",
    },
    "아폴로 베이글 (Apollo Bagels)": {
        "coord": [40.7516, -73.9902],
        "desc": "베이글 픽업 (224 W 35th St)",
        "icon": "cutlery",
    },
    # 옵션 A 장소
    "Buvette (옵션 A)": {
        "coord": [40.7341, -74.0029],
        "desc": "프렌치 감성 브런치 (42 Grove St)",
        "icon": "glass",
    },
    "L'Artusi (옵션 A)": {
        "coord": [40.7337, -74.0051],
        "desc": "이탈리안 파스타 런치 (228 W 10th St)",
        "icon": "cutlery",
    },
    "Caffe Panna (옵션 A 디저트)": {
        "coord": [40.7303, -73.9892],
        "desc": "수제 아이스크림 & 아포가토",
        "icon": "heart",
    },
    # 옵션 B 장소
    "L'Industrie Pizzeria (옵션 B)": {
        "coord": [40.7334, -74.0039],
        "desc": "뉴욕 1티어 조각 피자 (104 Christopher St)",
        "icon": "fire",
    },
    "Pommes Frites (옵션 B)": {
        "coord": [40.7299, -74.0006],
        "desc": "정통 벨기에식 감자튀김 (128 MacDougal St)",
        "icon": "cutlery",
    },
    "워싱턴 스퀘어 파크 (옵션 B)": {
        "coord": [40.7308, -73.9973],
        "desc": "피크닉 & 산책",
        "icon": "tree-conifer",
    },
}

# -------------------------------------------------------------
# 2. 레이아웃: 좌측 스케줄 / 우측 지도
# -------------------------------------------------------------
col_schedule, col_map = st.columns([1, 1.2], gap="large")

with col_schedule:
    st.subheader("🗓️ 여행 일정표")
    day_tab = st.radio(
        "날짜 선택", ["10/6 (화) - 콘서트 데이", "10/7 (수) - 웨스트 빌리지"], horizontal=True
    )

    if "10/6" in day_tab:
        active_day = "day1"
        st.markdown(
            """
            * **08:11 AM - 10:32 AM** | 비행 (ATL → EWR, Frontier #2282)
            * **10:32 AM - 12:00 PM** | EWR 공항 도착 후 맨해튼 이동 (우버)
            * **12:00 PM - 12:30 PM** | 📍 **호텔 도착 및 짐 보관** (Thompson Central Park)
            * **12:30 PM - 02:00 PM** | 📍 **점심 식사** (K-Town 한식)
            * **02:00 PM - 05:00 PM** | 📍 **센트럴 파크 산책** 및 콘서트 단장
            * **05:30 PM - 07:00 PM** | 저녁 식사 (냄새 안 배는 깔끔한 메뉴)
            * **07:30 PM** | 📍 **메디슨 스퀘어 가든 (MSG) 도착 & 입장**
            * **08:00 PM - 10:30 PM** | **몬스타엑스 콘서트 관람 🎤**
            * **10:30 PM -** | 📍 **호텔 복귀 (지하철 N/Q/R)**
            """
        )
        wv_opt = None

    else:
        active_day = "day2"
        st.markdown(
            """
            * **08:30 AM - 09:30 AM** | 호텔 조식 후 체크아웃 & **호텔에 짐 보관**
            * **10:00 AM - 11:00 AM** | 📍 **아폴로 베이글 픽업** (35th St)
            """
        )

        wv_opt = st.radio(
            "웨스트 빌리지 코스 선택",
            (
                "옵션 A: 시트다운 런치 & 디저트 (Buvette / L'Artusi + 카페)",
                "옵션 B: 스트리트 푸드 & 파크 (L'Industrie + Pommes Frites)",
            ),
        )

        if "옵션 A" in wv_opt:
            st.info(
                "🍽️ **옵션 A 세부 일정**\n"
                "- 11:30 AM - 01:30 PM: 📍 Buvette 또는 L'Artusi 런치\n"
                "- 01:30 PM - 03:30 PM: 📍 Caffe Panna 디저트 & 산책"
            )
        else:
            st.success(
                "🍕 **옵션 B 세부 일정**\n"
                "- 11:30 AM - 12:45 PM: 📍 L'Industrie Pizzeria (피자 포장/스탠딩)\n"
                "- 12:45 PM - 01:45 PM: 📍 Pommes Frites (감자튀김 테이크아웃)\n"
                "- 01:45 PM - 03:30 PM: 📍 워싱턴 스퀘어 파크 벤치 피크닉"
            )

        st.markdown(
            """
            * **04:30 PM - 05:30 PM** | 호텔 근처(미드타운) 복귀 & 가벼운 저녁
            * **05:45 PM - 06:15 PM** | 📍 **호텔 들러서 짐 픽업**
            * **06:30 PM** | 우버 탑승 후 EWR 공항 출발 (퇴근 트래픽 대비)
            * **10:29 PM - 01:01 AM** | 비행 (EWR → ATL, Frontier #1157)
            """
        )

# -------------------------------------------------------------
# 3. 지도 렌더링 (동선 경로 및 핀 포인트 생성)
# -------------------------------------------------------------
with col_map:
    st.subheader("🗺️ 일정별 동선 맵")

    # 표시할 포인트 순서 결정
    if active_day == "day1":
        route_keys = [
            "호텔 (Thompson Central Park)",
            "점심 (K-타운 한식)",
            "센트럴 파크",
            "콘서트장 (Madison Square Garden)",
            "호텔 (Thompson Central Park)",
        ]
        center_lat, center_lng = 40.7560, -73.9850
        zoom_level = 13
    else:
        if "옵션 A" in wv_opt:
            route_keys = [
                "호텔 (Thompson Central Park)",
                "아폴로 베이글 (Apollo Bagels)",
                "Buvette (옵션 A)",
                "L'Artusi (옵션 A)",
                "Caffe Panna (옵션 A 디저트)",
                "호텔 (Thompson Central Park)",
            ]
        else:
            route_keys = [
                "호텔 (Thompson Central Park)",
                "아폴로 베이글 (Apollo Bagels)",
                "L'Industrie Pizzeria (옵션 B)",
                "Pommes Frites (옵션 B)",
                "워싱턴 스퀘어 파크 (옵션 B)",
                "호텔 (Thompson Central Park)",
            ]
        center_lat, center_lng = 40.7450, -73.9950
        zoom_level = 13

    # Folium 지도 객체 생성
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=zoom_level,
        tiles="cartodbpositron",
    )

    # 핀 마커 및 동선 라인 좌표 수집
    polyline_coords = []
    for idx, key in enumerate(route_keys, start=1):
        loc = LOCATIONS[key]
        polyline_coords.append(loc["coord"])

        # 마커 추가
        folium.Marker(
            location=loc["coord"],
            popup=f"<b>#{idx}. {key}</b><br>{loc['desc']}",
            tooltip=f"#{idx}. {key}",
            icon=folium.Icon(
                color="red" if "콘서트" in key else "blue", icon=loc["icon"]
            ),
        ).add_to(m)

    # 동선 연결선 (점선)
    folium.PolyLine(
        locations=polyline_coords,
        color="#3388ff",
        weight=4,
        opacity=0.8,
        dash_array="8, 8",
    ).add_to(m)

    # Streamlit에 지도 렌더링
    st_folium(m, width="100%", height=560)