import streamlit as st
from sport_drawer.ucl_league_stage_drawer import UCLLeagueStageDrawer
from sport_drawer.club_world_cup_drawer import ClubWorldCupDrawer
from sport_drawer.world_cup_drawer import WorldCupDrawer

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

TOURNAMENTS = [
    {
        'name': 'FIFA World Cup',
        'drawer': WorldCupDrawer,
        'editions': [
            {
                'name': '2026',
                'data_path': './data/wc/teams_2026.json',
                'rules_url': 'https://digitalhub.fifa.com/m/2d1a1ac7bab78995/original/Draw-Procedures-for-the-FIFA-World-Cup-2026.pdf'
            }
        ]
    },
    {
        'name': 'FIFA Club World Cup',
        'drawer': ClubWorldCupDrawer,
        'editions': [
            {
                'name': '2025',
                'data_path': './data/club_wc/teams_2025.json',
                'rules_url': 'https://digitalhub.fifa.com/m/41ecaf295251d7c8/original/Draw-Procedures-for-the-FIFA-Club-World-Cup-2025.pdf'
            }
        ]
    },
    {
        'name': 'UEFA Champions League',
        'drawer': UCLLeagueStageDrawer,
        'editions': [
            {
                'name': '2025/26',
                'data_path': './data/ucl/teams_2025.json',
                'rules_url': 'https://editorial.uefa.com/resources/029c-1e95e1cbbcd9-9ddb0c4f9a94-1000/ucl_league_phase_draw_procedure.pdf'
            },
            {
                'name': '2024/25',
                'data_path': './data/ucl/teams_2024.json',
                'rules_url': 'https://editorial.uefa.com/resources/0290-1bb9a5f345c8-ac0c4b16a6b3-1000/202425_league_phase_draw_procedure.pdf'
            },
        ]
    },
    
]

# Initialize drawer_initialized flag only
if 'drawer_initialized' not in st.session_state:
    st.session_state.drawer_initialized = False

def on_tournament_change():
    st.session_state.drawer_initialized = True

def on_edition_change():
    st.session_state.drawer_initialized = True

# Sidebar selections
tournament = st.sidebar.selectbox(
    "Select Tournament",
    TOURNAMENTS,
    format_func=lambda x: x['name'],
    key='selected_tournament',
    on_change=on_tournament_change,
    index=0
)

edition = st.sidebar.selectbox(
    "Select Edition",
    tournament['editions'],
    format_func=lambda x: x['name'],
    key='selected_edition',
    on_change=on_edition_change
)

# Initialize drawer
drawer = tournament['drawer'](
    edition=edition['name'],
    teams_data_path=edition['data_path'],
    rules_url=edition['rules_url']
)

# Initialize session when tournament is changed
if st.session_state.drawer_initialized:
    drawer.init_session()
    st.session_state.drawer_initialized = False
    
drawer.run()