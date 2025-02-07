import os
from pathlib import Path
from typing import Any

import folium
import googlemaps
from dotenv import load_dotenv

from . import utils


class WaterStationMap:
    def __init__(self) -> None:  
        load_dotenv()
        self.GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAP_API")
        self.URL = "https://odws.hccg.gov.tw/001/Upload/25/opendata/9059/125/60744299-01ec-448b-86f7-f28b87c5c467.json"
        self.CENTER = [24.8041800737436, 120.97054960325579]
        self.gmaps = googlemaps.Client(key=self.GOOGLE_MAPS_API_KEY)

    def create_map(self) -> folium.Map:
        stations, map_data = self.load_water_stations()
        m = folium.Map(location=self.CENTER, zoom_start=13)

        css = """
<style>
.leaflet-popup-content-wrapper {
    padding: 0;
    border-radius: 8px;
    background: white;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.leaflet-popup-content {
    padding-left: 4px;
    margin: 0;
    width: auto !important;
    text-align: center;
}
.leaflet-popup-tip {
    background: white;
}
.station-info {
    font-family: 'Microsoft JhengHei', sans-serif;
    width: 250px;
}
.station-info h4 {
    margin: 0 0 8px 0;
    color: #333;
    font-size: 16px;
    font-weight: 600;
    padding-bottom: 8px;
    border-bottom: 2px solid #4299e1;
}
.station-info table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    line-height: 1.6;
    margin: auto;
}
.station-info td {
    padding: 6px 0;
    vertical-align: top;
}
.station-info td:first-child {
    padding-left: 1em;
    min-width: 80px;
    color: #666;
    font-weight: 500;
    text-align: left;
}
.station-info td:last-child {
    color: #333;
    text-align: left;
}
.copy-button {
    margin-top: 10px;
    background-color: #4299e1;
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    cursor: pointer;
    text-align: center;
    font-size: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    transition: background-color 0.3s;
}
.copy-button:hover {
    background-color: #3271b0;
}
.copy-toast {
    display: none;
    position: fixed;
    top: 7%;
    left: 50%;
    transform: translate(-50%, 0);
    background-color: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 12px 24px;
    border-radius: 24px;
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    z-index: 1000;
    animation: fadeInOut 2s ease-in-out;
}

@keyframes fadeInOut {
    0% { opacity: 0; transform: translate(-50%, -20px); }
    15% { opacity: 1; transform: translate(-50%, 0); }
    85% { opacity: 1; transform: translate(-50%, 0); }
    100% { opacity: 0; transform: translate(-50%, -20px); }
}
</style>
"""
        # 複製地址
        javascript = """
<script>
function createToastIfNotExists() {
    if (!document.getElementById('copy-toast')) {
        const toast = document.createElement('div');
        toast.id = 'copy-toast';
        toast.className = 'copy-toast';
        toast.textContent = '地址已複製';
        document.body.appendChild(toast);
    }
}

function showToast() {
    createToastIfNotExists();
    const toast = document.getElementById('copy-toast');

    // 重置動畫
    toast.style.animation = 'none';
    toast.offsetHeight; // 觸發 reflow
    toast.style.animation = 'fadeInOut 2s ease-in-out';

    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, 2000);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => {
            showToast();
        })
        .catch(err => {
            console.error('複製失敗:', err);
            alert('複製失敗，請手動複製');
        });
}

document.addEventListener('DOMContentLoaded', createToastIfNotExists);
</script>
"""
        m.get_root().header.add_child(folium.Element(css))  # type: ignore
        m.get_root().header.add_child(folium.Element(javascript))  # type: ignore

        # 標注加水站
        for station in stations:
            address = f"新竹市{station['營業地址']}"
            coords: Any = map_data["coordinates"].get(address)

            if coords:
                popup_content = f"""
<div class="station-info">
    <h4>{station["加水站名稱"]}</h4>
    <table>
        <tr>
            <td>公司名稱</td>
            <td>{station["公司名稱"]}</td>
        </tr>
        <tr>
            <td>地址</td>
            <td>新竹市{station["營業地址"]}</td>
        </tr>
        <tr>
            <td>水源</td>
            <td>{station["水源別"]}</td>
        </tr>
    </table>
    <div class="copy-button" onclick="copyToClipboard('新竹市{station["營業地址"]}')">複製地址</div>
</div>
"""

                folium.Marker(
                    location=[coords["lat"], coords["lng"]],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=station["加水站名稱"],
                ).add_to(m)

        return m

    def load_water_stations(self) -> tuple[Any, Any | dict[Any, Any]]:
        date = utils.get_date()
        stations_file = Path(f"data/water_stations_{date}.json")
        coords_file = Path(f"data/coordinates_{date}.json")

        stations = utils.read_file(stations_file)
        stations_online = utils.fetch_data(self.URL)
        stations_hash = utils.generate_hash(stations)
        stations_hash_online = utils.generate_hash(stations_online)
        map_data: Any | dict[Any, Any] = utils.read_file(coords_file) or {}

        # 檢查快取
        if stations_hash != stations_hash_online:
            stations = stations_online
            utils.write_file(stations, stations_file)
            map_data = {"hash": stations_hash, "coordinates": {}}
            for station in stations:
                address = f"新竹市{station['營業地址']}"
                try:
                    result = self.gmaps.geocode(address)  # type: ignore
                    if result:
                        location = result[0]["geometry"]["location"]
                        map_data["coordinates"][address] = {
                            "lat": location["lat"],
                            "lng": location["lng"],
                        }
                except Exception as e:
                    print(f"無法獲取地址坐標: {address}, 錯誤: {e!s}")

            utils.write_file(map_data, coords_file)

        return stations, map_data


def main() -> None:
    mapper = WaterStationMap()
    m = mapper.create_map()
    m.save("data/hsinchu-water-station.html")
    print("地圖已儲存到 hsinchu-water-station.html")


if __name__ == "__main__":
    main()
