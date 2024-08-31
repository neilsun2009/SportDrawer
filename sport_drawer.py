import streamlit as st
import json
import pandas as pd
import random
import copy
from collections import Counter

st.set_page_config(
    page_title='Champions League Drawer', 
    page_icon=':soccer:', 
    layout='wide',
    menu_items={
        'About': '''
        Developed by Bogo Sun @ [bogobogo.me](https://bogobogo.me/)
        
        Thanks to Darren Wang for the Siuuuuus!''',
    })

SIU_IMAGES = ['siu0.gif', 'siu1.gif', 'siu2.gif', 'siu3.gif', 'siu4.gif', 'siu5.gif', 'siu6.gif',]
MUELLER_IMAGES = ['mueller0.gif',]
SAD_IMAGES = ['sad0.png', 'sad1.png',]

st.title('🌟 UCL 2024 League Stage Drawer')

st.write('This is a simulator of the UEFA Champions League 2024 league stage draw.')
st.write('The rules are described in the [Official UEFA Procedure PDF](https://editorial.uefa.com/resources/0290-1bb9a5f345c8-ac0c4b16a6b3-1000/202425_league_phase_draw_procedure.pdf).')

# Load teams data
with open('./data/ucl_2024/teams.json', 'r', encoding='utf-8') as f:
    teams_data = json.load(f)
for idx, team in enumerate(teams_data):
    teams_data[idx]['id'] = idx
# Convert JSON to DataFrame
teams_df = pd.DataFrame(teams_data)
# convert json to id map
teams_id_map = {idx: team for idx, team in enumerate(teams_data)}
# Generate a map of team id to the number of teams of the same country
country_counts = Counter(team['country'] for team in teams_data)
team_country_counts = {team['id']: country_counts[team['country']] for team in teams_data}

def init_session():
    st.session_state['draw_round'] = 0
    st.session_state['drawn_team_ids'] = []
    # every team is represented by an ascii character 0 to 35
    # match state is compressed by sorting and concatenating all opponent pairs
    st.session_state['cur_state'] = ''
    # full state is a 36*8 matrix
    # each row is the opponent state of a team
    # 8 slots for home vs pot 1, away vs pot 1, home vs pot 2, away vs pot 2, ...
    st.session_state['cur_full_state'] = convert_full_state(st.session_state['cur_state'])
    st.session_state['cur_team'] = None
    # available draw status: waiting_draw, drawing, waiting_select, selecting, waiting_next_pot, waiting_done, done
    st.session_state['draw_status'] = 'waiting_draw'
    st.session_state['selecting_logs'] = []
    # newly selected team ids, for highlight them in the UI
    st.session_state['newly_sel_team_ids'] = []
    # whether no need to select, for skipping the selection process
    st.session_state['no_need_to_select'] = False
    st.toast('Ready to draw!', icon='📢')

# logic methods

def draw_new_team():
    if st.session_state['draw_status'] != 'waiting_draw':
        return
    st.session_state['draw_status'] = 'drawing'
    cur_pot = st.session_state['draw_round'] // 9 + 1
    
    available_team_ids = [idx for idx in range(len(teams_data)) if idx not in st.session_state['drawn_team_ids'] and teams_data[idx]['pot'] == cur_pot]
    drawn_team_id = random.choice(available_team_ids)
    
    st.session_state['drawn_team_ids'].append(drawn_team_id)
    st.session_state['cur_team'] = teams_id_map[drawn_team_id]
    st.session_state['newly_sel_team_ids'] = []
    # if len(st.session_state['drawn_team_ids']) == len(teams_data):
    #     st.session_state['draw_status'] = 'waiting_done'
    # elif len(st.session_state['cur_state']) == 8*len(teams_data):
    #     st.session_state['draw_status'] = 'autoselect'
    # else:
    if st.session_state['cur_full_state'][drawn_team_id].count(-1) == 0:
        st.session_state['no_need_to_select'] = True
        st.toast('No need to select opponents!', icon='🤐')
        if len(st.session_state['drawn_team_ids']) % 9 == 0:
            if len(st.session_state['drawn_team_ids']) == len(teams_data):
                st.session_state['draw_status'] = 'waiting_done'
            else:
                st.session_state['draw_status'] = 'waiting_next_pot'
        else:
            st.session_state['draw_round'] += 1
            st.session_state['draw_status'] = 'waiting_draw'
    else:
        st.session_state['no_need_to_select'] = False
        st.session_state['draw_status'] = 'waiting_select'
    # print(f"draw status: {st.session_state['draw_status']}")
    # print(f'len drawn team ids: {len(st.session_state["drawn_team_ids"])}')
    if st.session_state['cur_team']['name'] == 'FC Bayern München':
        st.toast("Mia san mia!", icon='❤️')
    else:
        st.toast(f"{st.session_state['cur_team']['name']}!", icon='🎉')
    
def convert_full_state(state):
    full_state = [([-1] * 8) for _ in range(len(teams_data))] 
    state_chunks = [state[i:i+2] for i in range(0, len(state), 2)]
    for chunk in state_chunks:
        team_id1, team_id2 = chunk
        team_id1 = ord(team_id1)
        team_id2 = ord(team_id2)
        pot1 = team_id1 // 9
        pot2 = team_id2 // 9
        # print(f'get team {team_id1} vs team {team_id2}')
        # print(f'pot1: {pot1}, pot2: {pot2}')
        full_state[team_id1][pot2 * 2] = team_id2
        full_state[team_id2][pot1 * 2 + 1] = team_id1
        # print(f'change full state row {team_id1} col {pot2 * 2} to {team_id2}')
        # print(f'change full state row {team_id2} col {pot1 * 2 + 1} to {team_id1}')
    return full_state

def convert_compressed_state(full_state):
    state_chunks = []
    for team_id1, row in enumerate(full_state):
        for idx, team_id2 in enumerate(row):
            if team_id2 != -1:
                if idx % 2 == 0:
                    state_chunks.append(chr(team_id1) + chr(team_id2))
                # else:
                #     state_chunks.append(chr(team_id2) + chr(team_id1))
    state_chunks = sorted(state_chunks)
    return ''.join(state_chunks)

def print_compressed_state(state):
    return '-'.join([str(ord(char)) for char in state])

def autofill_state(state):
    full_state = convert_full_state(state)
    for team_id, row in enumerate(full_state):
        team_pot = teams_id_map[team_id]['pot'] - 1
        team_country = teams_id_map[team_id]['country']
        country_count = get_country_count_by_opponents(row)
        invalid_countries = [country for country, count in country_count.items() if count >= 2]
        invalid_countries.append(team_country)
        for match_idx, opponent_id in enumerate(row):
            if opponent_id == -1:
                opponent_pot = match_idx // 2
                is_home = match_idx % 2 == 0
                available_team_ids = [i for i in range(len(teams_data)) if i not in row and i != team_id and teams_id_map[i]['pot'] == opponent_pot + 1 and teams_id_map[i]['country'] not in invalid_countries]
                available_team_ids = [i for i in available_team_ids if full_state[i][team_pot * 2 + (1 if is_home else 0)] == -1]
                for opponent_id in available_team_ids.copy():
                    opponent_country_count = get_country_count_by_opponents(full_state[opponent_id])
                    if team_country in opponent_country_count and opponent_country_count[team_country] >= 2:
                        available_team_ids.remove(opponent_id)
                if len(available_team_ids) == 0:
                    add_log(f"Autofill: no available team for team {teams_id_map[team_id]['name']} at match {match_idx + 1}, go back")
                    return None
                elif len(available_team_ids) == 1:
                    opponent_id = available_team_ids[0]
                    full_state[team_id][match_idx] = opponent_id
                    full_state[opponent_id][team_pot * 2 + (1 if is_home else 0)] = team_id
                    add_log(f"Autofill: {teams_id_map[team_id]['name']} vs {teams_id_map[opponent_id]['name']} at match {match_idx + 1}")
    return convert_compressed_state(full_state)

def get_country_count_by_opponents(opponent_ids):
    country_count = {}
    for opponent_id in opponent_ids:
        if opponent_id != -1:
            country = teams_id_map[opponent_id]['country']
            if country not in country_count:
                country_count[country] = 1
            else:
                country_count[country] += 1
    return country_count

def gen_possible_state(cur_team, cur_state, match_idx, drawn_team_ids, shuffle=True):
    # generate one possible combinations of opponents by dfs
    # first generate a possible solution match by match, then repeat the whole routine for each other team
    # to check if the solution is valid, we can check if the state is valid after all teams are processed
    # return current state if the solution is valid, otherwise return None
    
    cur_id = cur_team['id']
    cur_country = cur_team['country']
    cur_team_pot = cur_team['pot'] - 1 # 0-based
    cur_team_name = cur_team['name']
    cur_full_state = convert_full_state(cur_state)
    cur_team_opponents = cur_full_state[cur_id]
    
    if match_idx == 8:
        # reach the last match
        add_log(f"For team {cur_team_name} found possible opponents: {[teams_id_map[opponent]['name'] for opponent in cur_team_opponents]}")
        # check next team for validity
        max_country_count = 0
        next_team_id = -1        
        for i in range(len(teams_data)):
            if i not in drawn_team_ids:
                if team_country_counts[i] > max_country_count:
                    max_country_count = team_country_counts[i]
                    next_team_id = i
        if next_team_id == -1:
            # all teams are processed, solution is valid
            add_log(f"Found valid solution!")
            return cur_state
        # at this point, we don't need to shuffle the order of teams in order to make full use of state caches
        return gen_possible_state(teams_id_map[next_team_id], cur_state, 0, drawn_team_ids + [next_team_id], shuffle=True)
    
    add_log(f"Generating possible states for team {cur_team['name']} at match {match_idx + 1}")
    add_log(f"Current team opponents: {[teams_id_map[opponent]['name'] if opponent != -1 else 'TBD' for opponent in cur_team_opponents]}")
    if cur_team_opponents[match_idx] != -1:
        return gen_possible_state(cur_team, cur_state, match_idx + 1, drawn_team_ids, shuffle=shuffle)
    
    country_count = get_country_count_by_opponents(cur_team_opponents)
    invalid_countries = [country for country, count in country_count.items() if count == 2]
    invalid_countries.append(cur_country)
    match_pot = match_idx // 2
    match_is_home = match_idx % 2 == 0
    available_team_ids = [i for i in range(len(teams_data)) if i not in cur_team_opponents and i != cur_id and teams_id_map[i]['pot'] == match_pot + 1 and teams_id_map[i]['country'] not in invalid_countries]
    available_team_ids = [i for i in available_team_ids if cur_full_state[i][cur_team_pot * 2 + (1 if match_is_home else 0)] == -1]
    for opponent_id in available_team_ids.copy():
        opponent_country_count = get_country_count_by_opponents(cur_full_state[opponent_id])
        if cur_country in opponent_country_count and opponent_country_count[cur_country] >= 2:
            available_team_ids.remove(opponent_id)
    if shuffle:
        random.shuffle(available_team_ids)
    add_log(f"Available team ids: {available_team_ids}")
    if len(available_team_ids) == 0:
        add_log(f"No available team for team {cur_team['name']} at match {match_idx + 1}, go back")
        return None
    for opponent_id in available_team_ids:
        add_log(f"Trying team {teams_id_map[opponent_id]['name']} at match {match_idx + 1}")
        add_log(f'Its current opponents: {[teams_id_map[opponent]["name"] if opponent != -1 else "TBD" for opponent in cur_full_state[opponent_id]]}')
        # if cur_full_state[opponent_id][cur_team_pot * 2 + (1 if match_is_home else 0)] == -1:
        new_full_state = copy.deepcopy(cur_full_state)
        new_full_state[cur_id][match_idx] = opponent_id
        new_full_state[opponent_id][cur_team_pot * 2 + (1 if match_is_home else 0)] = cur_id
        new_state = convert_compressed_state(new_full_state)
        autofill_fail_flag = False
        while True:
            autofilled_state = autofill_state(new_state)
            if autofilled_state is None:
                add_log(f"Autofill reached a deadend for team {cur_team['name']} at match {match_idx + 1}, go back")
                autofill_fail_flag = True
                break
            if autofilled_state == new_state:
                break
            new_state = autofilled_state
        if autofill_fail_flag:
            continue
        result = gen_possible_state(cur_team, new_state, match_idx + 1, drawn_team_ids, shuffle=shuffle)
        if result is not None:
            return result
        else:
            continue
    add_log(f"No valid team found for team {cur_team['name']} at match {match_idx + 1}, go back")
    return None
   
def select_opponents():
    cur_team = st.session_state['cur_team']
    st.session_state['draw_status'] = 'selecting'
    st.session_state['selecting_logs'] = []
    original_sel_team_ids = [idx for idx in st.session_state['cur_full_state'][cur_team['id']] if idx != -1]
    
    possible_states = []
    choice_state = gen_possible_state(cur_team, st.session_state['cur_state'], 0, st.session_state['drawn_team_ids'])
    if choice_state is None:
        raise Exception('No possible state found!')
    add_log(f"Choose state: {print_compressed_state(choice_state)}")
    choice_full_state = convert_full_state(choice_state)
    # choose only matches that are related to the current team
    opponent_ids = choice_full_state[cur_team['id']]
    # update current state by opponent ids
    cur_full_state = st.session_state['cur_full_state']
    for match_idx, opponent_id in enumerate(opponent_ids):
        add_log(f"Final result: vs {teams_id_map[opponent_id]['name']} at match {match_idx + 1}")
        is_home = match_idx % 2 == 0
        cur_full_state[cur_team['id']][match_idx] = opponent_id
        cur_full_state[opponent_id][teams_id_map[cur_team['id']]['pot'] * 2 - 2 + (1 if is_home else 0)] = cur_team['id']
    st.session_state['cur_state'] = convert_compressed_state(cur_full_state)
    
    st.session_state['newly_sel_team_ids'] = [idx for idx in opponent_ids if idx not in original_sel_team_ids]
        
    if len(st.session_state['drawn_team_ids']) % 9 == 0:
        if len(st.session_state['drawn_team_ids']) == len(teams_data):
            st.session_state['draw_status'] = 'waiting_done'
        else:
            st.session_state['draw_status'] = 'waiting_next_pot'
    else:
        st.session_state['draw_round'] += 1
        st.session_state['draw_status'] = 'waiting_draw'
    
    # print(f"draw status: {st.session_state['draw_status']}")
    # print(f'len drawn team ids: {len(st.session_state["drawn_team_ids"])}')
    
    if cur_team['name'] == 'FC Bayern München':
        st.toast("#ESMUELLERT", icon='2️⃣')
    else:
        st.toast("Siuuuuu!!!", icon='7️⃣')
   
def finish_draw():
    st.session_state['draw_status'] = 'done'
    st.balloons()  
    
def draw_next_pot():
    st.session_state['draw_status'] = 'waiting_draw'
    st.session_state['draw_round'] += 1
    
# display methods
    
def add_log(log):
    st.session_state['selecting_logs'].append(log)
    
def st_print_opponents_by_team_id(team_id, size='small', hide_header=False, transpose=False, highlight_ids=None):
    col_match_idx_map = {}
    row_num = 3 if transpose else 5
    col_num = 5 if transpose else 3
    for row_idx in range(row_num):
        if hide_header and row_idx == 0:
            continue
        cols = st.columns([1] + [3] * (col_num-1), vertical_alignment='center')
        if row_idx == 0:
            if transpose:
                for col_idx in range(1, col_num):
                    cols[col_idx].write(f"Pot {col_idx}")
            else:
                cols[1].write('Home')
                cols[2].write('Away')
        else:
            for col_idx, col in enumerate(cols):
                if col_idx == 0:
                    if transpose:
                        col.write('Home' if row_idx == 1 else 'Away')
                    else:
                        col.write(f"Pot {row_idx}")
                else:
                    if transpose:
                        col_match_idx_map[(col_idx-1) * 2 + row_idx - 1] = col
                    else:
                        col_match_idx_map[(row_idx-1) * 2 + col_idx - 1] = col
    
    if highlight_ids is None:
        highlight_ids = []  
    for match_idx, opponent_id in enumerate(st.session_state['cur_full_state'][team_id]):
        with col_match_idx_map[match_idx]:
            st_display_team(opponent_id, size=size, highlight=opponent_id in highlight_ids, available=opponent_id != -1)
   
def get_team_logo_html(logo_url, height=100, width=None, alt='logo', inline=False):
    if width is None:
        width = 'auto' # this will create a centered effect
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
    
def get_country_flag_html(country, size=15):
    NATION_CODE_MAP = {
        'ENG': 'gb-eng',
        'SCO': 'gb-sct',
        'GER': 'de',
        'ESP': 'es',
        'ITA': 'it',
        'FRA': 'fr',
        'POR': 'pt',
        'NED': 'nl',
        'BEL': 'be',
        'UKR': 'ua',
        'AUT': 'at',
        'SUI': 'ch',
        'CZE': 'cz',
        'CRO': 'hr',
        'SRB': 'rs',
        'SVK': 'sk',
    }
    if country not in NATION_CODE_MAP:
        url = 'https://hatscripts.github.io/circle-flags/flags/xx.svg'
    # elif country in ['ESP']:
    #     url = f'https://flagicons.lipis.dev/flags/4x3/{NATION_CODE_MAP[country]}.svg'
    else:
        url = f'https://flagicons.lipis.dev/flags/4x3/{NATION_CODE_MAP[country]}.svg'
    # return f'''
    # <div style="width: {size}px; height: {size}px; border-radius: 100%; overflow: hidden; display: inline-flex; margin: 2px; box-shadow: 0 0 0 2px rgba(0, 0, 0, .08);">
    #     <img src="{url}" alt="{country}" style="width: 100%; height: 100%; object-fit: cover; object-position: center;" />
    # </div>
    # '''
    return f'''
    <div style="width: {size/3*4}px; height: {size}px; display: inline-flex; margin: 2px; box-shadow: 0 0 0 2px rgba(0, 0, 0, .08);">
        <img src="{url}" alt="{country}" style="width: 100%; height: 100%; object-fit: cover; object-position: center;" />
    </div>
    '''
    
def st_display_team(team_id, size='big', available=True, highlight=False):
    if team_id == -1:
        team = {'name': 'TBD', 'logo': 'https://hatscripts.github.io/circle-flags/flags/xx.svg', 'country': 'XX'}
    else:
        team = teams_id_map[team_id]
    
    if size == 'huge':
        core_html = (f"""
            <div style='margin-top:10px'></div>
            {get_team_logo_html(team['logo'], height=300, alt=team['name'])}
            <div style='text-align: center;margin-top: 5px'>
                <big><b>{team['name']}</b></big><br/>
                {get_country_flag_html(team['country'])}<br/>
                 &nbsp;{'🏆'*team.get('champions', 0)}&nbsp;
            </div>""")
    elif size == 'big':
        core_html = (f"""
            <div style='margin-top:10px'></div>
            {get_team_logo_html(team['logo'], alt=team['name'])}
            <div style='text-align: center;margin-top: 5px'>
                <big><b>{team['name']}</b></big><br/>
                {get_country_flag_html(team['country'])}<br/>
                 &nbsp;{'🏆'*team.get('champions', 0)}&nbsp;
            </div>""")
    else:
        core_html = (f"""<div style='text-align: left;display: flex;justify-content: left;align-items: center;'>
                {get_team_logo_html(team['logo'], height=30, width=30, alt=team['name'], inline=True)}&nbsp;&nbsp;
                <span>{team['name']}</span>
            </div>""")
    with st.container(border=True):
        st.html(f"""<div style="
                        padding: 2px;
                        opacity: {1 if available else 0.5}; 
                        background-color: {'rgba(0,106,255,0.2)' if highlight else 'auto'}
                    ">{core_html}</div>""")

# init
if 'draw_round' not in st.session_state:
    init_session()
    
# teams
st.header('⚽ Meet the teams')
with st.container():
    team_pot_tabs = st.tabs([f'Pot {i+1}' for i in range(4)])
    for pot, tab in enumerate(team_pot_tabs):
        with tab:
            pot_teams = [team for team in teams_data if team['pot'] == pot + 1]
            for row_idx in range(0, len(pot_teams), 3):
                row_teams = pot_teams[row_idx:row_idx+3]
                columns = st.columns(3)
                for col_idx, team in enumerate(row_teams):
                    with columns[col_idx]:
                        st_display_team(team['id'])
            

# draw
if st.session_state['draw_status'] != 'done':
    st.header('🎲 Draw now!')
    
    if st.session_state['draw_status'] == 'waiting_done':
        st.button('Finish!', on_click=finish_draw, type='primary')
    if st.session_state['draw_status'] == 'waiting_next_pot':
        st.button('Next pot', on_click=draw_next_pot, type='primary')
    
    draw_col, sel_col = st.columns([1, 1], gap='medium')
    cur_pot = st.session_state['draw_round'] // 9 + 1
    cur_pot_team_ids = [team['id'] for team in teams_data if team['pot'] == cur_pot]
    available_team_ids = [idx for idx in cur_pot_team_ids if idx not in st.session_state['drawn_team_ids']]
    
    with draw_col:
        btn_title = f"Draw #{st.session_state['draw_round'] % 9 + 1} from Pot {cur_pot}"
        if st.session_state['draw_status'] == 'drawing':
            btn_title = 'Drawing...'
        elif st.session_state['draw_status'] == 'waiting_done':
            btn_title = 'All teams are drawn!'
        elif st.session_state['draw_status'] == 'waiting_next_pot':
            btn_title = f'All teams from Pot {cur_pot} are drawn!'
            
        st.button(btn_title, 
            type='primary',
            disabled=st.session_state['draw_status'] != 'waiting_draw',
            on_click=draw_new_team)
        if st.session_state['cur_team'] and st.session_state['draw_status'] not in ['drawing'] \
                and len(available_team_ids) < 9:
            st.write(f"**{st.session_state['cur_team']['name']}** is drawn!")
            st_display_team(st.session_state['cur_team']['id'], highlight=True)
        st.write(f'**Teams from Pot {cur_pot}:**')
        for row_idx in range(0, len(cur_pot_team_ids), 3):
            row_team_ids = cur_pot_team_ids[row_idx:row_idx+3]
            columns = st.columns(3)
            for col_idx, team_id in enumerate(row_team_ids):
                with columns[col_idx]:
                    st_display_team(team_id, size='small', available=team_id in available_team_ids,)
                                    # highlight=team_id == st.session_state['cur_team']['id'] if st.session_state['cur_team'] else False)

    with sel_col:
        # see if we need to select opponents
        st.button('Draw opponents',
            type='primary',
            disabled=st.session_state['draw_status'] != 'waiting_select',
            on_click=select_opponents)
        if st.session_state['cur_team'] and st.session_state['draw_status'] not in ['drawing'] and len(available_team_ids) < 9:            
            if st.session_state['draw_status'] == 'selecting':
                with st.spinner('Drawing opponents...'):
                    while True:
                        pass
            if st.session_state['draw_status'] in ['waiting_draw', 'waiting_next_pot', 'waiting_done']:
                st.write(f'Opponents for **{st.session_state["cur_team"]["name"]}** are drawn!')
                if st.session_state['no_need_to_select']:
                    image_name = random.choice(SAD_IMAGES)
                elif st.session_state['cur_team']['name'] == 'FC Bayern München':
                    image_name = random.choice(MUELLER_IMAGES)
                else:
                    image_name = random.choice(SIU_IMAGES)
                st.image(f'static/{image_name}')
            st.write(f"**Fixtures for {st.session_state['cur_team']['name']}**:")
            st_print_opponents_by_team_id(st.session_state['cur_team']['id'], highlight_ids=st.session_state['newly_sel_team_ids'])
            
            if st.session_state['draw_status'] != 'waiting_select':
                with st.status('Loading drawing logs...'):
                    for log in st.session_state['selecting_logs']:
                        st.write(log)
                        
                
if st.session_state['draw_status'] == 'done':
    st.header('🏆 Draw result!')
else:
    st.header('📺 Current status')
with st.container():
    # st.subheader('By pot')
    result_pot_tabs = st.tabs([f'Pot {i+1}' for i in range(4)])
    for pot, tab in enumerate(result_pot_tabs):
        with tab:
            pot_teams = [team for team in teams_data if team['pot'] == pot + 1]
            for team in pot_teams:
                team_col, opponents_col = st.columns([1, 3], vertical_alignment='center', gap='medium')
                with team_col:
                    st_display_team(team['id'], size='big')
                with opponents_col:
                    st_print_opponents_by_team_id(team['id'], hide_header=False, transpose=True)
                st.write('---')
    
    # st.subheader('By team')
    # sorted_teams_data = sorted(teams_data, key=lambda x: x['name'])
    # sel_team = st.selectbox('Select a team', sorted_teams_data, format_func=lambda x: x['name'], label_visibility='collapsed')
    # st_display_team(sel_team['id'], size='huge')
    # st.write(f"**Opponents for {sel_team['name']}:**")
    # st_print_opponents_by_team_id(sel_team['id'], size='big')
    
st.button('Restart', on_click=init_session, type='primary')