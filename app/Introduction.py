import base64
import geopandas as gpd
from PIL import Image
import plotly.express as px
import requests
import streamlit as st

from io import BytesIO

# demo-pictures from the global repo
url_1 = "https://raw.githubusercontent.com/ekatef/assets/master/preview_1.png"
url_2 = "https://raw.githubusercontent.com/ekatef/assets/master/preview_2.png"
url_3 = "https://raw.githubusercontent.com/ekatef/assets/master/preview_3.png"

@st.cache_data
def get_image(url):
    r = requests.get(url)
    return BytesIO(r.content)

def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://raw.githubusercontent.com/drifter089/pypsa-lit-docs/main/static/img/logo.png);
                background-repeat: no-repeat;
                padding-top: 30px;
                background-position: 20px 20px;
                background-size: 70px;
            [data-testid="stSidebarNav"]::before {
                content: "test";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def resize_image(img, target_width, target_height, fill_color=(255, 255, 255)):
    aspect = img.width / img.height
    new_width = target_width
    new_height = target_height

    if aspect > 1:
        new_height = int(target_width / aspect)
    elif aspect < 1:
        new_width = int(target_height * aspect)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    return(img)    

st.title("Welcome to the Energy Transition Explorer!")

image_1 = Image.open(get_image(url=url_1))
image_2 = Image.open(get_image(url=url_2))
image_3 = Image.open(get_image(url=url_3))

image_1_resized = resize_image(image_1, 200, 300)
image_2_resized = resize_image(image_2, 200, 300)
image_3_resized = resize_image(image_3, 200, 300)

st.image(
    [image_1_resized, image_2_resized, image_3_resized], 
    width=200)

st.header("Select a page from the sidebar to get started")

st.subheader("This is a prototype of the Energy Transition Explorer. You can view the code on [GitHub](https://github.com/pypsa-meets-earth/pypsa-earth-lit)")

add_logo()
