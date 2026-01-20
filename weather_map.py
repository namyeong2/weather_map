import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

# 1. 전국 주요 지역 좌표 및 격자 데이터 확장
locations = {
    "서울": {"lat": 37.5665, "lon": 126.9780, "nx": 60, "ny": 127},
    "인천": {"lat": 37.4563, "lon": 126.7052, "nx": 55, "ny": 124},
    "대전": {"lat": 36.3504, "lon": 127.3845, "nx": 67, "ny": 134},
    "대구": {"lat": 35.8714, "lon": 128.6014, "nx": 89, "ny": 90},
    "광주": {"lat": 35.1595, "lon": 126.8526, "nx": 58, "ny": 74},
    "부산": {"lat": 35.1796, "lon": 129.0756, "nx": 98, "ny": 76},
    "울산": {"lat": 35.5384, "lon": 129.3114, "nx": 102, "ny": 84},
    "세종": {"lat": 36.4800, "lon": 127.2890, "nx": 66, "ny": 103},
    "경기도": {"lat": 37.2752, "lon": 127.0095, "nx": 60, "ny": 120},
    "강원도": {"lat": 37.8854, "lon": 127.7298, "nx": 73, "ny": 134},
    "충청북도": {"lat": 36.6350, "lon": 127.4912, "nx": 69, "ny": 107},
    "충청남도": {"lat": 36.6588, "lon": 126.6728, "nx": 68, "ny": 100},
    "전라북도": {"lat": 35.8204, "lon": 127.1088, "nx": 63, "ny": 89},
    "전라남도": {"lat": 34.8160, "lon": 126.4629, "nx": 51, "ny": 67},
    "경상북도": {"lat": 36.5760, "lon": 128.5056, "nx": 89, "ny": 91},
    "경상남도": {"lat": 35.2377, "lon": 128.6922, "nx": 91, "ny": 77},
    "제주도": {"lat": 33.4996, "lon": 126.5312, "nx": 52, "ny": 38}
}

st.set_page_config(page_title="전국 동네 기온 지도", layout="wide")
st.title("🗺️ 지도에서 찾는 우리 동네 기온")
st.info("지도의 마커를 클릭하거나 아래 목록에서 지역을 선택하세요.")

# 2. 지역 선택 방식 다변화 (지도 클릭 OR 드롭다운 메뉴)
selected_city = st.selectbox("직접 지역 선택하기", list(locations.keys()))

# 3. 포리움 지도 생성 및 마커 최적화
m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles="OpenStreetMap")

for name, info in locations.items():
    folium.Marker(
        location=[info["lat"], info["lon"]],
        popup=name,
        tooltip=name,
        icon=folium.Icon(color="blue", icon="info-sign") # 마커 아이콘 명시적 설정
    ).add_to(m)

# 지도를 화면에 표시하고 클릭 이벤트 감지
output = st_folium(m, width="100%", height=500)

# 마커를 클릭했다면 해당 지역으로 자동 변경
if output["last_object_clicked_popup"]:
    selected_city = output["last_object_clicked_popup"]

st.subheader(f"📍 현재 선택된 지역: {selected_city}")

# 4. 날씨 확인 및 출력
if st.button(f"{selected_city} 실시간 기온 조회"):
    auth_key = "f0cc4e1eb2f7f6c3613c93bcecf0e5e554ef9bd38070521b661234849bfd1791"
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
    
    nx, ny = locations[selected_city]["nx"], locations[selected_city]["ny"]
    now = datetime.now()
    
    params = {
        'serviceKey': auth_key,
        'dataType': 'JSON',
        'base_date': now.strftime("%Y%m%d"),
        'base_time': now.strftime("%H00"),
        'nx': nx,
        'ny': ny
    }

    try:
        response = requests.get(url, params=params)
        res_data = response.json()
        items = res_data['response']['body']['items']['item']
        
        for item in items:
            if item['category'] == 'T1H': # 기온 항목
                st.metric(label=f"{selected_city} 현재 기온", value=f"{item['obsrValue']} °C")
                
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다. (API 승인 대기 중일 수 있습니다.)")