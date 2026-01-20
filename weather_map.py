!pip install streamlit folium streamlit-folium
import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

# 1. 지역별 좌표 및 격자 데이터 정의
locations = {
    "대전(본부)": {"lat": 36.3504, "lon": 127.3845, "nx": 67, "ny": 134},
    "서울": {"lat": 37.5665, "lon": 126.9780, "nx": 60, "ny": 127},
    "부산": {"lat": 35.1796, "lon": 129.0756, "nx": 98, "ny": 76},
    "제주": {"lat": 33.4996, "lon": 126.5312, "nx": 52, "ny": 38}
}

st.set_page_config(page_title="지도 기반 날씨 알림이", layout="wide")
st.title("🗺️ 지도에서 찾는 우리 동네 기온")
st.info("지도의 마커를 클릭하여 지역을 선택한 후 버튼을 눌러주세요.")

# 2. 포리움 지도 생성
# 한국 중심부로 초기 위치 설정
m = folium.Map(location=[36.5, 127.5], zoom_start=7)

# 각 지역별로 마커 추가
for name, info in locations.items():
    folium.Marker(
        location=[info["lat"], info["lon"]],
        popup=name,
        tooltip=f"{name} 날씨 보기"
    ).add_to(m)

# 3. Streamlit에 지도 표시 및 클릭 이벤트 감지
# 지도를 표시하고 클릭된 마커의 정보를 가져옵니다.
output = st_folium(m, width=700, height=500)

# 클릭된 마커의 이름을 확인 (기본값은 '대전(본부)')
selected_city = "대전(본부)"
if output["last_object_clicked_popup"]:
    selected_city = output["last_object_clicked_popup"]

st.subheader(f"📍 현재 선택된 지역: {selected_city}")

# 4. 날씨 확인 버튼 및 API 호출 로직
if st.button(f"{selected_city} 기온 조회하기"):
    auth_key = "f0cc4e1eb2f7f6c3613c93bcecf0e5e554ef9bd38070521b661234849bfd1791"
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'

    # 좌표 가져오기
    nx = locations[selected_city]["nx"]
    ny = locations[selected_city]["ny"]

    # 시간 설정
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
                st.metric(label=f"{selected_city} 기온", value=f"{item['obsrValue']} °C")
                st.success(f"{selected_city}의 실시간 날씨 정보를 성공적으로 가져왔습니다.")
    except Exception as e:
        st.error(f"데이터 호출 중 오류 발생: {e}")