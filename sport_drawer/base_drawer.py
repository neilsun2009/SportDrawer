import streamlit as st
import json
import pandas as pd
import random
import copy
from collections import Counter
from abc import ABC, abstractmethod

class BaseDrawer(ABC):
    
    tournament = 'Bogo Cup'
    highlight_color = 'rgba(0, 106, 255, 0.2)'
    
    def __init__(self, edition, teams_data_path, rules_url=None):
        """
        Initialize base drawer with configuration
        """
        self.edition = edition
        self.teams_data_path = teams_data_path
        self.rules_url = rules_url
        self.setup_page()
        self.load_teams()
        
    def setup_page(self):        
        st.title(f'🎰 {self.tournament} Drawer')
        st.write(f'This is a drawer simulator of the {self.edition} season.')
        if self.rules_url:
            st.write(f'The rules are described in the [Official Rules]({self.rules_url}).')

    def load_teams(self):
        """Load and process teams data"""
        with open(self.teams_data_path, 'r', encoding='utf-8') as f:
            self.teams_data = json.load(f)
        for idx, team in enumerate(self.teams_data):
            self.teams_data[idx]['id'] = idx
        self.teams_df = pd.DataFrame(self.teams_data)
        self.teams_id_map = {idx: team for idx, team in enumerate(self.teams_data)}

    def init_session(self):
        """Initialize session state with basic drawing variables"""
        st.session_state['draw_status'] = 'waiting_draw'
        st.session_state['drawn_team_ids'] = []
        st.session_state['cur_team'] = None
        st.session_state['selecting_logs'] = []
        self.init_custom_session()
        st.toast('Ready to draw!', icon='📢')

    @abstractmethod
    def init_custom_session(self):
        """Initialize format-specific session variables"""
        pass

    @abstractmethod
    def draw_new_team(self):
        """Draw a new team according to format rules"""
        pass

    def get_team_logo_html(self, logo_url, height=100, width=None, alt='logo', inline=False):
        """Generate HTML for team logo display"""
        if width is None:
            width = 'auto'
        else:
            width = f'{width}px'
        height = f'{height}px'
        img_core = f'<img src="{logo_url}" alt={alt} width="100%" height="100%" style="object-fit:contain">'
        if inline:
            return f'''<span style="width:{width};height:{height}">
                    {img_core}
                </span>'''
        else:
            return f'''<div style="width:{width};height:{height}">
                    {img_core}
                </div>'''

    def get_country_flag_html(self, country, size=15):
        """Generate HTML for country flag display"""
        NATION_CODE_MAP = {
            'ENG': 'gb-eng', 'SCO': 'gb-sct', 'GER': 'de', 'ESP': 'es',
            'ITA': 'it', 'FRA': 'fr', 'POR': 'pt', 'NED': 'nl',
            'BEL': 'be', 'UKR': 'ua', 'AUT': 'at', 'SUI': 'ch',
            'CZE': 'cz', 'CRO': 'hr', 'SRB': 'rs', 'SVK': 'sk',
            'ARG': 'ar', 'BRA': 'br', 'CHL': 'cl', 'MEX': 'mx',
            'USA': 'us', 'KSA': 'sa', 'JPN': 'jp', 'KOR': 'kr',
            'UAE': 'ae', 'EGY': 'eg', 'MAR': 'ma', 'NZL': 'nz',
            'TUN': 'tn', 'RSA': 'za',
        }
        code = NATION_CODE_MAP.get(country, 'xx')
        url = f'https://flagicons.lipis.dev/flags/4x3/{code}.svg'
        return f'''
        <div style="width: {size*4/3}px; height: {size}px; display: inline-flex; margin: 2px; box-shadow: 0 0 0 2px rgba(0, 0, 0, .08);">
            <img src="{url}" alt="{country}" style="width: 100%; height: 100%; object-fit: cover; object-position: center;" />
        </div>
        '''

    def st_display_team(self, team_id, size='big', available=True, highlight=False):
        """Display team information in Streamlit"""
        if team_id == -1:
            team = {'name': 'TBD', 'logo': 'https://hatscripts.github.io/circle-flags/flags/xx.svg', 'country': 'XX'}
        else:
            team = self.teams_id_map[team_id]
        
        if size == 'huge':
            core_html = (f"""
                <div style='margin-top:10px'></div>
                {self.get_team_logo_html(team['logo'], height=300, alt=team['name'])}
                <div style='text-align: center;margin-top: 5px'>
                    <big><b>{team['name']}</b></big><br/>
                    {self.get_country_flag_html(team['country'])}<br/>
                     &nbsp;{'🏆'*team.get('champions', 0)}&nbsp;
                </div>""")
        elif size == 'big':
            core_html = (f"""
                <div style='margin-top:10px'></div>
                {self.get_team_logo_html(team['logo'], alt=team['name'])}
                <div style='text-align: center;margin-top: 5px'>
                    <big><b>{team['name']}</b></big><br/>
                    {self.get_country_flag_html(team['country'])}<br/>
                     &nbsp;{'🏆'*team.get('champions', 0)}&nbsp;
                </div>""")
        else:
            core_html = (f"""<div style='text-align: left;display: flex;justify-content: left;align-items: center;'>
                    {self.get_team_logo_html(team['logo'], height=30, width=30, alt=team['name'], inline=True)}&nbsp;&nbsp;
                    <span>{team['name']}</span>
                </div>""")
        
        with st.container(border=True):
            st.html(f"""<div style="
                            padding: 2px;
                            opacity: {1 if available else 0.5}; 
                            background-color: {self.highlight_color if highlight else 'auto'}
                        ">{core_html}</div>""")

    def add_log(self, log):
        """Add a log message to the selection logs"""
        st.session_state['selecting_logs'].append(log)

    def run(self):
        """Main drawing interface"""
        if 'draw_status' not in st.session_state:
            self.init_session()

        # Display teams section
        self.display_teams()

        # Draw section
        if st.session_state['draw_status'] != 'done':
            self.display_draw_interface()

        # Results section
        self.display_results()

        st.button('Restart', on_click=self.init_session, type='primary')

    @abstractmethod
    def display_teams(self):
        """Display all teams in the tournament"""
        pass

    @abstractmethod
    def display_draw_interface(self):
        """Display the drawing interface"""
        pass

    @abstractmethod
    def display_results(self):
        """Display draw results"""
        pass 