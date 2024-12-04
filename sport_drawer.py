import streamlit as st
from sport_drawer.ucl_drawer import UCLDrawer
from sport_drawer.worldcup_drawer import WorldCupDrawer

st.set_page_config(
    page_title='Tournament Drawer', 
    page_icon='⚽', 
    layout='wide',
    menu_items={
        'About': '''
        Developed by Bogo Sun @ [bogobogo.me](https://bogobogo.me/)
        
        Thanks to Darren Wang for the Siuuuuus!''',
    },
    initial_sidebar_state='collapsed'
)

drawer_type = st.sidebar.selectbox(
    "Select Tournament",
    ["UEFA Champions League", "FIFA World Cup"]
)

if drawer_type == "UEFA Champions League":
    drawer = UCLDrawer()
else:
    drawer = WorldCupDrawer()

drawer.run()