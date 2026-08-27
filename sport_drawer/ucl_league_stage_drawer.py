from .base_drawer import BaseDrawer
import streamlit as st
import random
import copy
from collections import Counter

class UCLLeagueStageDrawer(BaseDrawer):
    
    tournament = 'UEFA Champions League (League Stage)'
    highlight_color = 'rgba(0, 106, 255, 0.2)'
    
    def __init__(self, edition, teams_data_path, rules_url=None):
        self.SIU_IMAGES = ['siu0.gif', 'siu1.gif', 'siu2.gif', 'siu3.gif', 'siu4.gif', 'siu5.gif', 'siu6.gif']
        self.MUELLER_IMAGES = ['mueller0.gif']
        self.SAD_IMAGES = ['sad0.png', 'sad1.png']
        
        super().__init__(edition, teams_data_path, rules_url)
        
    def init_custom_session(self):
        """Initialize UCL-specific session variables"""
        st.session_state['draw_round'] = 0
        st.session_state['cur_state'] = ''
        st.session_state['cur_full_state'] = self.convert_full_state(st.session_state['cur_state'])
        st.session_state['newly_sel_team_ids'] = []
        st.session_state['no_need_to_select'] = False

    def convert_full_state(self, state):
        """Convert compressed state to full state matrix"""
        full_state = [([-1] * 8) for _ in range(len(self.teams_data))] 
        state_chunks = [state[i:i+2] for i in range(0, len(state), 2)]
        for chunk in state_chunks:
            team_id1, team_id2 = chunk
            team_id1 = ord(team_id1)
            team_id2 = ord(team_id2)
            pot1 = team_id1 // 9
            pot2 = team_id2 // 9
            full_state[team_id1][pot2 * 2] = team_id2
            full_state[team_id2][pot1 * 2 + 1] = team_id1
        return full_state

    def convert_compressed_state(self, full_state):
        """Convert full state matrix to compressed state"""
        state_chunks = []
        for team_id1, row in enumerate(full_state):
            for idx, team_id2 in enumerate(row):
                if team_id2 != -1 and idx % 2 == 0:
                    state_chunks.append(chr(team_id1) + chr(team_id2))
        state_chunks = sorted(state_chunks)
        return ''.join(state_chunks)

    def draw_new_team(self):
        """Draw a new team from current pot"""
        if st.session_state['draw_status'] != 'waiting_draw':
            return
            
        st.session_state['draw_status'] = 'drawing'
        cur_pot = st.session_state['draw_round'] // 9 + 1
        
        available_team_ids = [
            idx for idx in range(len(self.teams_data)) 
            if idx not in st.session_state['drawn_team_ids'] 
            and self.teams_data[idx]['pot'] == cur_pot
        ]
        
        drawn_team_id = random.choice(available_team_ids)
        st.session_state['drawn_team_ids'].append(drawn_team_id)
        st.session_state['cur_team'] = self.teams_id_map[drawn_team_id]
        st.session_state['newly_sel_team_ids'] = []
        st.session_state['selecting_logs'] = []

        if st.session_state['cur_full_state'][drawn_team_id].count(-1) == 0:
            st.session_state['no_need_to_select'] = True
            st.toast('No need to select opponents!', icon='🤐')
            if len(st.session_state['drawn_team_ids']) % 9 == 0:
                if len(st.session_state['drawn_team_ids']) == len(self.teams_data):
                    st.session_state['draw_status'] = 'waiting_done'
                else:
                    st.session_state['draw_status'] = 'waiting_next_pot'
            else:
                st.session_state['draw_round'] += 1
                st.session_state['draw_status'] = 'waiting_draw'
        else:
            st.session_state['no_need_to_select'] = False
            st.session_state['draw_status'] = 'waiting_select'

        if st.session_state['cur_team']['name'] == 'FC Bayern München':
            st.toast("Mia san mia!", icon='❤️')
        else:
            st.toast(f"{st.session_state['cur_team']['name']}!", icon='🎉')

    def select_opponents(self):
        """Select opponents for the drawn team"""
        cur_team = st.session_state['cur_team']
        st.session_state['draw_status'] = 'selecting'
        original_sel_team_ids = [idx for idx in st.session_state['cur_full_state'][cur_team['id']] if idx != -1]
        
        choice_state = self.gen_possible_state(cur_team, st.session_state['cur_state'], 0, st.session_state['drawn_team_ids'])
        if choice_state is None:
            raise Exception('No possible state found!')
            
        self.add_log(f"Choose state: {'-'.join([str(ord(char)) for char in choice_state])}")
        choice_full_state = self.convert_full_state(choice_state)
        
        opponent_ids = choice_full_state[cur_team['id']]
        cur_full_state = st.session_state['cur_full_state']
        
        for match_idx, opponent_id in enumerate(opponent_ids):
            self.add_log(f"Final result: vs {self.teams_id_map[opponent_id]['name']} at match {match_idx + 1}")
            is_home = match_idx % 2 == 0
            cur_full_state[cur_team['id']][match_idx] = opponent_id
            cur_full_state[opponent_id][self.teams_id_map[cur_team['id']]['pot'] * 2 - 2 + (1 if is_home else 0)] = cur_team['id']
            
        st.session_state['cur_state'] = self.convert_compressed_state(cur_full_state)
        st.session_state['newly_sel_team_ids'] = [idx for idx in opponent_ids if idx not in original_sel_team_ids]
        
        if len(st.session_state['drawn_team_ids']) % 9 == 0:
            if len(st.session_state['drawn_team_ids']) == len(self.teams_data):
                st.session_state['draw_status'] = 'waiting_done'
            else:
                st.session_state['draw_status'] = 'waiting_next_pot'
        else:
            st.session_state['draw_round'] += 1
            st.session_state['draw_status'] = 'waiting_draw'
            
        if cur_team['name'] == 'FC Bayern München':
            st.toast("#ESMUELLERT", icon='2️⃣')
        else:
            st.toast("Siuuuuu!!!", icon='7️⃣')

    def display_teams(self):
        """Display all teams grouped by pot"""
        st.header('⚽ Meet the teams')
        team_pot_tabs = st.tabs([f'Pot {i+1}' for i in range(4)])
        for pot, tab in enumerate(team_pot_tabs):
            with tab:
                pot_teams = [team for team in self.teams_data if team['pot'] == pot + 1]
                for row_idx in range(0, len(pot_teams), 3):
                    row_teams = pot_teams[row_idx:row_idx+3]
                    columns = st.columns(3)
                    for col_idx, team in enumerate(row_teams):
                        with columns[col_idx]:
                            self.st_display_team(team['id'])

    def display_draw_interface(self):
        """Display the drawing interface"""
        st.header('🎲 Draw now!')
        
        if st.session_state['draw_status'] == 'waiting_done':
            st.button('Finish!', on_click=self.finish_draw, type='primary')
        if st.session_state['draw_status'] == 'waiting_next_pot':
            st.button('Next pot', on_click=self.draw_next_pot, type='primary')
        
        draw_col, sel_col = st.columns([1, 1], gap='medium')
        self.display_draw_column(draw_col)
        self.display_selection_column(sel_col)

    def display_results(self):
        """Display current draw results"""
        if st.session_state['draw_status'] == 'done':
            st.header('🏆 Draw result!')
        else:
            st.header('📺 Current status')
            
        result_pot_tabs = st.tabs([f'Pot {i+1}' for i in range(4)])
        for pot, tab in enumerate(result_pot_tabs):
            with tab:
                self.display_pot_results(pot)

    def get_country_count_by_opponents(self, opponent_ids):
        """Get count of teams from each country in opponent list"""
        country_count = {}
        for opponent_id in opponent_ids:
            if opponent_id != -1:
                country = self.teams_id_map[opponent_id]['country']
                country_count[country] = country_count.get(country, 0) + 1
        return country_count

    def autofill_state(self, state):
        """Automatically fill in obvious matches in the state"""
        full_state = self.convert_full_state(state)
        for team_id, row in enumerate(full_state):
            team_pot = self.teams_id_map[team_id]['pot'] - 1
            team_country = self.teams_id_map[team_id]['country']
            country_count = self.get_country_count_by_opponents(row)
            invalid_countries = [country for country, count in country_count.items() if count >= 2]
            invalid_countries.append(team_country)
            
            for match_idx, opponent_id in enumerate(row):
                if opponent_id == -1:
                    opponent_pot = match_idx // 2
                    is_home = match_idx % 2 == 0
                    available_team_ids = [
                        i for i in range(len(self.teams_data)) 
                        if i not in row and i != team_id 
                        and self.teams_id_map[i]['pot'] == opponent_pot + 1 
                        and self.teams_id_map[i]['country'] not in invalid_countries
                    ]
                    available_team_ids = [
                        i for i in available_team_ids 
                        if full_state[i][team_pot * 2 + (1 if is_home else 0)] == -1
                    ]
                    
                    for opponent_id in available_team_ids.copy():
                        opponent_country_count = self.get_country_count_by_opponents(full_state[opponent_id])
                        if team_country in opponent_country_count and opponent_country_count[team_country] >= 2:
                            available_team_ids.remove(opponent_id)
                            
                    if len(available_team_ids) == 0:
                        self.add_log(f"Autofill: no available team for team {self.teams_id_map[team_id]['name']} at match {match_idx + 1}, go back")
                        return None
                    elif len(available_team_ids) == 1:
                        opponent_id = available_team_ids[0]
                        full_state[team_id][match_idx] = opponent_id
                        full_state[opponent_id][team_pot * 2 + (1 if is_home else 0)] = team_id
                        self.add_log(f"Autofill: {self.teams_id_map[team_id]['name']} vs {self.teams_id_map[opponent_id]['name']} at match {match_idx + 1}")
        
        return self.convert_compressed_state(full_state)

    def gen_possible_state(self, cur_team, cur_state, match_idx, drawn_team_ids, shuffle=True):
        """Generate possible match combinations using DFS"""
        cur_id = cur_team['id']
        cur_country = cur_team['country']
        cur_team_pot = cur_team['pot'] - 1
        cur_team_name = cur_team['name']
        cur_full_state = self.convert_full_state(cur_state)
        cur_team_opponents = cur_full_state[cur_id]

        if match_idx == 8:
            self.add_log(f"For team {cur_team_name} found possible opponents: {[self.teams_id_map[opponent]['name'] for opponent in cur_team_opponents]}")
            # Find next team to process
            next_team_id = -1
            max_country_count = 0
            for i in range(len(self.teams_data)):
                if i not in drawn_team_ids:
                    country_count = sum(1 for team in self.teams_data if team['country'] == self.teams_data[i]['country'])
                    if country_count > max_country_count:
                        max_country_count = country_count
                        next_team_id = i
            
            if next_team_id == -1:
                self.add_log(f"Found valid solution!")
                return cur_state
                
            return self.gen_possible_state(
                self.teams_id_map[next_team_id], 
                cur_state, 
                0, 
                drawn_team_ids + [next_team_id], 
                shuffle=True
            )

        self.add_log(f"Generating possible states for team {cur_team['name']} at match {match_idx + 1}")
        self.add_log(f"Current team opponents: {[self.teams_id_map[opponent]['name'] if opponent != -1 else 'TBD' for opponent in cur_team_opponents]}")
        
        if cur_team_opponents[match_idx] != -1:
            return self.gen_possible_state(cur_team, cur_state, match_idx + 1, drawn_team_ids, shuffle=shuffle)
        
        country_count = self.get_country_count_by_opponents(cur_team_opponents)
        invalid_countries = [country for country, count in country_count.items() if count >= 2]
        invalid_countries.append(cur_country)
        
        match_pot = match_idx // 2
        match_is_home = match_idx % 2 == 0
        
        available_team_ids = [
            i for i in range(len(self.teams_data)) 
            if i not in cur_team_opponents and i != cur_id 
            and self.teams_id_map[i]['pot'] == match_pot + 1 
            and self.teams_id_map[i]['country'] not in invalid_countries
        ]
        
        available_team_ids = [
            i for i in available_team_ids 
            if cur_full_state[i][cur_team_pot * 2 + (1 if match_is_home else 0)] == -1
        ]
        
        for opponent_id in available_team_ids.copy():
            opponent_country_count = self.get_country_count_by_opponents(cur_full_state[opponent_id])
            if cur_country in opponent_country_count and opponent_country_count[cur_country] >= 2:
                available_team_ids.remove(opponent_id)
                
        if shuffle:
            random.shuffle(available_team_ids)
            
        self.add_log(f"Available team ids: {available_team_ids}")
        
        if len(available_team_ids) == 0:
            self.add_log(f"No available team for team {cur_team['name']} at match {match_idx + 1}, go back")
            return None
            
        for opponent_id in available_team_ids:
            self.add_log(f"Trying team {self.teams_id_map[opponent_id]['name']} at match {match_idx + 1}")
            self.add_log(f'Its current opponents: {[self.teams_id_map[opponent]["name"] if opponent != -1 else "TBD" for opponent in cur_full_state[opponent_id]]}')
            
            new_full_state = copy.deepcopy(cur_full_state)
            new_full_state[cur_id][match_idx] = opponent_id
            new_full_state[opponent_id][cur_team_pot * 2 + (1 if match_is_home else 0)] = cur_id
            new_state = self.convert_compressed_state(new_full_state)
            
            autofill_fail_flag = False
            while True:
                autofilled_state = self.autofill_state(new_state)
                if autofilled_state is None:
                    self.add_log(f"Autofill reached a deadend for team {cur_team['name']} at match {match_idx + 1}, go back")
                    autofill_fail_flag = True
                    break
                if autofilled_state == new_state:
                    break
                new_state = autofilled_state
                
            if autofill_fail_flag:
                continue
                
            result = self.gen_possible_state(cur_team, new_state, match_idx + 1, drawn_team_ids, shuffle=shuffle)
            if result is not None:
                return result
                
        self.add_log(f"No valid team found for team {cur_team['name']} at match {match_idx + 1}, go back")
        return None

    def display_draw_column(self, col):
        """Display the draw column interface"""
        with col:
            cur_pot = st.session_state['draw_round'] // 9 + 1
            cur_pot_team_ids = [team['id'] for team in self.teams_data if team['pot'] == cur_pot]
            available_team_ids = [idx for idx in cur_pot_team_ids if idx not in st.session_state['drawn_team_ids']]
            
            btn_title = f"Draw #{st.session_state['draw_round'] % 9 + 1} from Pot {cur_pot}"
            if st.session_state['draw_status'] == 'drawing':
                btn_title = 'Drawing...'
            elif st.session_state['draw_status'] == 'waiting_done':
                btn_title = 'All teams are drawn!'
            elif st.session_state['draw_status'] == 'waiting_next_pot':
                btn_title = f'All teams from Pot {cur_pot} are drawn!'
                
            st.button(
                btn_title,
                type='primary',
                disabled=st.session_state['draw_status'] != 'waiting_draw',
                on_click=self.draw_new_team
            )

            if st.session_state['cur_team'] and st.session_state['draw_status'] not in ['drawing'] \
                    and len(available_team_ids) < 9:
                st.write(f"**{st.session_state['cur_team']['name']}** is drawn!")
                self.st_display_team(st.session_state['cur_team']['id'], highlight=True)
                
            st.write(f'**Teams from Pot {cur_pot}:**')
            for row_idx in range(0, len(cur_pot_team_ids), 3):
                row_team_ids = cur_pot_team_ids[row_idx:row_idx+3]
                columns = st.columns(3)
                for col_idx, team_id in enumerate(row_team_ids):
                    with columns[col_idx]:
                        self.st_display_team(
                            team_id, 
                            size='small', 
                            available=team_id in available_team_ids
                        )

    def display_selection_column(self, col):
        """Display the selection column interface"""
        with col:
            st.button(
                'Draw opponents',
                type='primary',
                disabled=st.session_state['draw_status'] != 'waiting_select',
                on_click=self.select_opponents
            )
            
            cur_pot = st.session_state['draw_round'] // 9 + 1
            cur_pot_team_ids = [team['id'] for team in self.teams_data if team['pot'] == cur_pot]
            available_team_ids = [idx for idx in cur_pot_team_ids if idx not in st.session_state['drawn_team_ids']]

            if st.session_state['cur_team'] and st.session_state['draw_status'] not in ['drawing'] \
                    and len(available_team_ids) < 9:
                if st.session_state['draw_status'] == 'selecting':
                    with st.spinner('Drawing opponents...'):
                        while True:
                            pass

                if st.session_state['draw_status'] in ['waiting_draw', 'waiting_next_pot', 'waiting_done']:
                    st.write(f'Opponents for **{st.session_state["cur_team"]["name"]}** are drawn!')
                    if st.session_state['no_need_to_select']:
                        image_name = random.choice(self.SAD_IMAGES)
                    elif st.session_state['cur_team']['name'] == 'FC Bayern München':
                        image_name = random.choice(self.MUELLER_IMAGES)
                    else:
                        image_name = random.choice(self.SIU_IMAGES)
                    st.image(f'static/{image_name}')

                st.write(f"**Fixtures for {st.session_state['cur_team']['name']}**:")
                self.st_print_opponents_by_team_id(
                    st.session_state['cur_team']['id'], 
                    highlight_ids=st.session_state['newly_sel_team_ids']
                )

                # if st.session_state['draw_status'] != 'waiting_select':
                #     with st.status('Loading drawing logs...'):
                #         for log in st.session_state['selecting_logs']:
                #             st.write(log)

    def display_pot_results(self, pot):
        """Display results for a specific pot"""
        pot_teams = [team for team in self.teams_data if team['pot'] == pot + 1]
        for team in pot_teams:
            team_col, opponents_col = st.columns([1, 3], vertical_alignment='center', gap='medium')
            with team_col:
                self.st_display_team(team['id'], size='big')
            with opponents_col:
                self.st_print_opponents_by_team_id(team['id'], hide_header=False, transpose=True)
            st.write('---')

    def st_print_opponents_by_team_id(self, team_id, size='small', hide_header=False, transpose=False, highlight_ids=None):
        """Display opponents for a team"""
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
                self.st_display_team(
                    opponent_id, 
                    size=size, 
                    highlight=opponent_id in highlight_ids, 
                    available=opponent_id != -1
                )

    def finish_draw(self):
        """Finish the draw process"""
        st.session_state['draw_status'] = 'done'
        st.balloons()

    def draw_next_pot(self):
        """Move to next pot"""
        st.session_state['draw_status'] = 'waiting_draw'
        st.session_state['draw_round'] += 1

    # Helper methods...