import streamlit as st
from sport_drawer.ucl_league_stage_drawer import UCLLeagueStageDrawer
from sport_drawer.club_world_cup_drawer import ClubWorldCupDrawer

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
                'name': '2024/25',
                'data_path': './data/ucl/teams_2024.json',
                'rules_url': 'https://editorial.uefa.com/resources/0290-1bb9a5f345c8-ac0c4b16a6b3-1000/202425_league_phase_draw_procedure.pdf'
            }
        ]
    },
    
]

tournament = st.sidebar.selectbox(
    "Select Tournament",
    TOURNAMENTS,
    format_func=lambda x: x['name']
)
edition = st.sidebar.selectbox(
    "Select Edition",
    tournament['editions'],
    format_func=lambda x: x['name']
)

drawer = tournament['drawer'](
    edition=edition['name'],
    teams_data_path=edition['data_path'],
    rules_url=edition['rules_url']
)

drawer.run()