import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NYC Bachelorette Trip",
    page_icon="🗽",
    layout="wide",
)

st.title("🗽 NYC Bachelorette Trip (10/6 - 10/7)")

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.subheader("🗓️ 여행 일정표")
    
    tab_day1, tab_day2 = st.tabs(["10/6 (화) - 콘서트 데이", "10/7 (수) - 웨스트 빌리지"])
    
    with tab_day1:
        st.markdown(
            """
            * **08:11 AM - 10:32 AM** | 비행 (ATL → EWR, Frontier #2282)
            * **10:32 AM - 12:00 PM** | EWR 공항 착륙 후 맨해튼 이동 (우버)
            * **12:00 PM - 12:30 PM** | Thompson Central Park 도착 및 체크인/짐 보관
            * **12:30 PM - 02:00 PM** | 점심 식사 (피로 회복용 한식)
            * **02:00 PM - 05:00 PM** | 센트럴 파크 산책 및 콘서트 준비
            * **05:30 PM - 07:00 PM** | 저녁 식사 (냄새 안 나는 깔끔한 메뉴)
            * **07:30 PM** | 메디슨 스퀘어 가든 (MSG) 입장
            * **08:00 PM - 10:30 PM** | **몬스타엑스 콘서트 관람**
            * **10:30 PM -** | 호텔 복귀 및 휴식
            """
        )
        day1_selected = st.checkbox("10/6 동선 지도로 보기", value=False)
        
    with tab_day2:
        st.markdown(
            """
            * **08:30 AM - 09:30 AM** | 호텔 조식 후 체크아웃 & **호텔 짐 보관**
            * **10:00 AM - 11:00 AM** | 아폴로 베이글 (224 W 35th St) 픽업
            """
        )
        
        wv_option = st.radio(
            "웨스트 빌리지 코스 선택:",
            (
                "옵션 A: 시트다운 런치 & 디저트 (Buvette / L'Artusi + 카페)",
                "옵션 B: 스트리트 푸드 투어 (L'Industrie + Pommes Frites + 공원)",
            ),
            index=0,
        )
        
        if "옵션 A" in wv_option:
            st.info(
                "🍽️ **옵션 A 세부 일정**\n"
                "- 11:30 AM - 01:30 PM: Buvette 또는 L'Artusi 점심\n"
                "- 01:30 PM - 03:30 PM: Caffe Panna 또는 Magnolia Bakery 디저트 & 산책"
            )
        else:
            st.success(
                "🍕 **옵션 B 세부 일정**\n"
                "- 11:30 AM - 12:45 PM: L'Industrie Pizzeria (조각 피자)\n"
                "- 12:45 PM - 01:45 PM: Pommes Frites (벨기에식 감자튀김)\n"
                "- 01:45 PM - 03:30 PM: 워싱턴 스퀘어 파크 피크닉 & 커피"
            )
            
        st.markdown(
            """
            * **04:30 PM - 05:30 PM** | 미드타운 복귀 및 가벼운 저녁
            * **05:45 PM - 06:15 PM** | Thompson Central Park 들러 **짐 픽업**
            * **06:30 PM** | 우버 탑승 후 EWR 공항으로 이동 (트래픽 대비)
            * **10:29 PM - 01:01 AM** | 비행 (EWR → ATL, Frontier #1157)
            """
        )

with col2:
    st.subheader("🗺️ 동선 경로 맵")
    
    if tab_day1 and 'day1_selected' in locals() and day1_selected:
        origin = "Thompson+Central+Park+New+York"
        destination = "Madison+Square+Garden+New+York"
        waypoints = "Koreatown+Manhattan+New+York"
        map_title = "10/6 동선: 호텔 ➔ K-타운 ➔ MSG"
    else:
        origin = "Thompson+Central+Park+New+York"
        waypoints = "Apollo+Bagels+New+York"
        
        if "옵션 A" in wv_option:
            destination = "Buvette+New+York"
            map_title = "10/7 옵션 A 동선: 호텔 ➔ 아폴로베이글 ➔ Buvette (웨스트빌리지)"
        else:
            destination = "Pommes+Frites+New+York"
            waypoints += "|L'Industrie+Pizzeria+West+Village+New+York"
            map_title = "10/7 옵션 B 동선: 호텔 ➔ 아폴로베이글 ➔ L'Industrie ➔ Pommes Frites"

    st.caption(f"📍 현재 표시 경로: **{map_title}**")
    
    embed_url = f"https://maps.google.com/maps?saddr={origin}&daddr={destination}&waypoints={waypoints}&output=embed"
    
    components.iframe(embed_url, height=580, scrolling=True)
    
    st.link_button(
        "Google Maps 앱에서 경로 열기",
        f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}",
    )
