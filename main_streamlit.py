import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import streamlit as st
from azure.cosmos import CosmosClient
import json
import base64


@dataclass
class StatsRow:
    timestamp: datetime
    humidity: Optional[float]
    temperature: Optional[float]


st.title('IoT monitoring')


@st.cache_resource
def init_connection() -> CosmosClient:
    endpoint = st.secrets["cosmos"]["endpoint"]
    key = st.secrets["cosmos"]["key"]
    return CosmosClient(url=endpoint, credential=key)


connection = init_connection()


def encode_dict(base64str: str) -> dict:
    return json.loads(base64.b64decode(base64str))


def get_sensor_data() -> pd.DataFrame:
    container = connection.get_database_client("IoTHub").get_container_client("SensorData")
    return pd.DataFrame(
        (StatsRow(
            timestamp=datetime.strptime(record["SystemProperties"]["iothub-enqueuedtime"], "%Y-%m-%dT%H:%M:%S.%f0Z"),
            humidity=encode_dict(record["Body"]).get("humidity", None),
            temperature=encode_dict(record["Body"]).get("temperature", None)) for record in container.read_all_items()))


def get_latest_data(data: pd.DataFrame, records_count: int = 10) -> pd.DataFrame:
    return data.sort_values(by=["timestamp"], ascending=False).head(records_count)


placeholder = st.empty()
datetime_slider = st.slider(
    "Last minutes to show:",
    key="datetime_slider",
    value=15,
    min_value=1,
    max_value=360)
while True:
    with placeholder.container():
        st.caption("Last update time: {}".format(datetime.fromtimestamp(time.time())))
        sensor_data = get_sensor_data()
        latest_data = get_latest_data(sensor_data)
        st.subheader("Last 10 records")
        st.write(latest_data.set_index(latest_data.columns[0]))
        filtered_data = sensor_data[
            sensor_data['timestamp'] > datetime.fromtimestamp(time.time()) - timedelta(minutes=datetime_slider)]
        st.subheader("Last {} minutes graph".format(datetime_slider))
        st.line_chart(filtered_data, x="timestamp", y=["humidity", "temperature"])
        time.sleep(5)
