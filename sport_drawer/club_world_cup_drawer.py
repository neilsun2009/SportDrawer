from sport_drawer.base_drawer import BaseDrawer
import streamlit as st
import random
import copy

class ClubWorldCupDrawer(BaseDrawer):
    
    tournament = 'FIFA Club World Cup'
    highlight_color = 'rgba(241, 190, 72, 0.8)'
    
    def __init__(self, edition, teams_data_path, rules_url=None):
        self.groups = {chr(65+i): [] for i in range(8)}  # Groups A through H
        # Define pathways for knockout phase
        self.pathway1_groups = ['A', 'C', 'E', 'G']  # Winners paired with runners-up from pathway 2
        self.pathway2_groups = ['B', 'D', 'F', 'H']  # Winners paired with runners-up from pathway 1
        
        # Celebration images
        self.SIU_IMAGES = ['siu0.gif', 'siu1.gif', 'siu2.gif', 'siu3.gif', 'siu4.gif', 'siu5.gif', 'siu6.gif']
        self.MUELLER_IMAGES = ['mueller0.gif']
        self.SAD_IMAGES = ['sad0.png', 'sad1.png']
        
        super().__init__(edition, teams_data_path, rules_url)
        
    def init_custom_session(self):
        """Initialize Club World Cup-specific session variables"""
        st.session_state['current_pot'] = 1
        st.session_state['groups'] = {chr(65+i): [] for i in range(8)}  # Groups A through H
        st.session_state['selecting_logs'] = []
        
        # Pre-allocate host teams
        host_teams = [t for t in self.teams_data if 'host' in t and t['host']]
        for team in host_teams:
            if team['name'] == 'Inter Miami':
                st.session_state['groups']['A'].append(team['id'])
                st.toast(f"{team['name']} pre-allocated to Group A!", icon='🎉')
            elif team['name'] == 'Seattle Sounders':
                st.session_state['groups']['B'].append(team['id'])
                st.toast(f"{team['name']} pre-allocated to Group B!", icon='🎉')
            st.session_state['drawn_team_ids'].append(team['id'])
        
    def get_confed_allocation_state(self):
        """Get current state of confederation allocations in groups"""
        state = {group: {
            'UEFA': [], 'CONMEBOL': [], 'AFC': [], 
            'CAF': [], 'CONCACAF': [], 'OFC': []
        } for group in self.groups}
        
        for group, team_ids in st.session_state['groups'].items():
            for team_id in team_ids:
                team = self.teams_id_map[team_id]
                state[group][team['confed']].append(team)
                
        return state
    
    def check_possible_allocation(self, team, confed_state, group, drawn_team_ids):
        """Check if allocating team to this group leads to a valid solution"""
        print(f"Checking allocation of {team['name']} to Group {group}")
        # Create new state with this allocation
        new_state = copy.deepcopy(confed_state)
        new_state[group][team['confed']].append(team)
        
        # If this is the last team in pot, this allocation is valid
        if len(drawn_team_ids) == len([t for t in self.teams_data if t['pot'] == team['pot']]):
            return True
        
        # Find next team to process
        next_team_id = -1
        for t in self.teams_data:
            if t['pot'] == team['pot'] and t['id'] not in drawn_team_ids:
                next_team_id = t['id']
                break
        
        if next_team_id == -1:
            return True
            
        # Try to find at least one valid group for next team
        next_team = self.teams_id_map[next_team_id]
        remaining_groups = [g for g in self.groups if g != group]
        
        # Try each remaining group for the next team
        for next_group in remaining_groups:
            if self.can_join_group(next_team, next_group, new_state):
                if self.check_possible_allocation(
                    next_team,
                    new_state,
                    next_group,
                    drawn_team_ids + [next_team_id]
                ):
                    return True
        print(f"Allocation of {team['name']} to Group {group} is not possible")
        return False

    def get_available_groups(self, team):
        """Get available groups for a team based on constraints"""
                
        # For all teams, check each group individually
        confed_state = self.get_confed_allocation_state()
        available_groups = []
        
        # Check each group individually
        for group in self.groups:
            if len(st.session_state['groups'][group]) < 4 and self.can_join_group(team, group, confed_state):
                print(f"Team {team['name']} Group {group} is available")
                # For each candidate group, verify that choosing it won't lead to a deadend
                if self.check_possible_allocation(team, confed_state, group, st.session_state['drawn_team_ids']):
                    available_groups.append(group)
                    
        return available_groups

    def can_join_group(self, team, group, allocation_state):
        """Check if a team can join a group based on constraints"""
        # Get group teams from allocation state
        group_teams = []
        for confed in allocation_state[group]:
            group_teams.extend(allocation_state[group][confed])
        
        # Check if group is full
        if len(group_teams) >= 4:
            return False
            
        # Check if group already has a team from the same pot
        if any(t['pot'] == team['pot'] for t in group_teams):
            return False
            
        # Special checks for pot 1
        if team['pot'] == 1:
            if team['confed'] in ['UEFA', 'CONMEBOL'] and team['confed_rank'] <= 4:
                # Define valid group pairs for top UEFA/CONMEBOL teams
                group_pairs = {
                    'A': 'C', 'C': 'A',
                    'B': 'D', 'D': 'B',
                    'E': 'G', 'G': 'E',
                    'F': 'H', 'H': 'F'
                }
                paired_group = group_pairs.get(group)
                if not paired_group:
                    return False
                
                # Check if this is a top 1-2 or 3-4 team
                is_top_two = team['confed_rank'] <= 2
                
                # Get all allocated top teams in both pathways
                pathway1_teams = []
                pathway2_teams = []
                for g, teams in allocation_state.items():
                    for confed in ['UEFA', 'CONMEBOL']:
                        for t in teams[confed]:
                            if t['pot'] == 1 and t['confed_rank'] <= 4:
                                if g in self.pathway1_groups:
                                    pathway1_teams.append(t)
                                else:
                                    pathway2_teams.append(t)
                
                current_pathway_teams = pathway1_teams if group in self.pathway1_groups else pathway2_teams
                
                # Check if same confederation rank pair (1-2 or 3-4) is already in this pathway
                for t in current_pathway_teams:
                    if t['confed'] == team['confed'] and (t['confed_rank'] <= 2) == is_top_two:
                        return False
                
                # Check paired group constraints
                paired_group_teams = []
                for confed in ['UEFA', 'CONMEBOL']:
                    paired_group_teams.extend(allocation_state[paired_group][confed])
                
                for t in paired_group_teams:
                    if t['pot'] == 1:
                        # Cannot pair same confederation
                        if t['confed'] == team['confed']:
                            return False
                        # Cannot pair teams from same rank pairs (1-2 vs 1-2 or 3-4 vs 3-4)
                        if (t['confed_rank'] <= 2) == is_top_two:
                            return False
            
        # Check confederation constraints
        if team['confed'] == 'UEFA':
            uefa_count = len(allocation_state[group]['UEFA'])
            if uefa_count >= 2:
                return False
        else:
            confed_count = len(allocation_state[group][team['confed']])
            if confed_count >= 1:
                return False
                
        # Check country constraints
        if any(t['country'] == team['country'] for t in group_teams):
            return False
            
        # Special checks for pot 2
        if team['pot'] == 2:
            if team['confed'] == 'UEFA':
                # UEFA teams 5-8 must be with CONMEBOL 1-4
                if team['confed_rank'] >= 5 and team['confed_rank'] <= 8:
                    conmebol_teams = [t for t in allocation_state[group]['CONMEBOL'] 
                                    if t['confed_rank'] <= 4]
                    if not conmebol_teams:
                        return False
                # UEFA teams 9-12 must be with UEFA 1-4
                elif team['confed_rank'] >= 9:
                    uefa_teams = [t for t in allocation_state[group]['UEFA'] 
                                if t['confed_rank'] <= 4]
                    if not uefa_teams:
                        return False
            
        return True

    def draw_new_team(self):
        """Draw a new team from current pot"""
        if st.session_state['draw_status'] != 'waiting_draw':
            return
            
        st.session_state['draw_status'] = 'drawing'
        cur_pot = st.session_state['current_pot']
        
        available_team_ids = [
            idx for idx in range(len(self.teams_data)) 
            if idx not in st.session_state['drawn_team_ids'] 
            and self.teams_data[idx]['pot'] == cur_pot
        ]
        
        drawn_team_id = random.choice(available_team_ids)
        drawn_team = self.teams_id_map[drawn_team_id]
        
        st.session_state['drawn_team_ids'].append(drawn_team_id)
        st.session_state['cur_team'] = drawn_team
        
        # Automatically assign to first available group
        available_groups = self.get_available_groups(drawn_team)
        if not available_groups:
            raise Exception(f"No valid group found for {drawn_team['name']}!")
            
        group = available_groups[0]
        st.session_state['groups'][group].append(drawn_team_id)
        
        # Calculate how many teams have been drawn in current pot (excluding pre-allocated hosts)
        cur_pot_drawn_count = len([
            t for t in st.session_state['drawn_team_ids'] 
            if self.teams_id_map[t]['pot'] == cur_pot 
        ])
        
        st.toast(f"{drawn_team['name']} drawn to Group {group}!", icon='🎉')
        
        # Check if pot is complete (8 teams per pot)
        if cur_pot_drawn_count == 8:
            if cur_pot == 4:
                st.session_state['draw_status'] = 'waiting_done'
            else:
                st.session_state['draw_status'] = 'waiting_next_pot'
        else:
            st.session_state['draw_status'] = 'waiting_draw'

    def display_teams(self):
        """Display all teams grouped by pot"""
        st.header('⚽ Meet the teams')
        team_pot_tabs = st.tabs([f'Pot {i+1}' for i in range(4)])
        
        for pot, tab in enumerate(team_pot_tabs):
            with tab:
                pot_teams = [team for team in self.teams_data if team['pot'] == pot + 1]
                for row_idx in range(2):  # 2 rows
                    cols = st.columns(4)  # 4 columns
                    for col_idx in range(4):
                        team_idx = row_idx * 4 + col_idx
                        if team_idx < len(pot_teams):
                            with cols[col_idx]:
                                self.st_display_team(pot_teams[team_idx]['id'])

    def display_draw_interface(self):
        """Display the drawing interface"""
        st.header('🎲 Draw now!')
        
        if st.session_state['draw_status'] == 'waiting_done':
            st.button('Finish!', on_click=self.finish_draw, type='primary')
        if st.session_state['draw_status'] == 'waiting_next_pot':
            st.button('Next pot', on_click=self.draw_next_pot, type='primary')
        
        # Calculate current team number in pot (excluding pre-allocated hosts)
        cur_pot = st.session_state['current_pot']
        cur_pot_drawn_count = len([
            t for t in st.session_state['drawn_team_ids'] 
            if self.teams_id_map[t]['pot'] == cur_pot 
        ])
        
        btn_title = f"Draw team #{cur_pot_drawn_count + 1} from Pot {cur_pot}"
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
        
        draw_col, group_col = st.columns(2)
        self.display_draw_column(draw_col)
        self.display_group_column(group_col)

    def display_draw_column(self, col):
        """Display current pot and drawn team"""
        with col:
            cur_pot = st.session_state['current_pot']
            pot_teams = [team for team in self.teams_data if team['pot'] == cur_pot]
            available_team_ids = [t['id'] for t in pot_teams if t['id'] not in st.session_state['drawn_team_ids']]
            
            if st.session_state['cur_team'] and st.session_state['draw_status'] not in ['drawing'] \
                    and len(available_team_ids) < 8:  # Changed from 9 to 8
                st.write(f"**{st.session_state['cur_team']['name']}** is drawn!")
                self.st_display_team(st.session_state['cur_team']['id'], highlight=True)
                
            st.write(f'**Teams from Pot {cur_pot}:**')
            # Display 4x2 grid of teams from current pot only
            for row_idx in range(4):
                cols = st.columns(2)
                for col_idx in range(2):
                    team_idx = row_idx * 2 + col_idx
                    if team_idx < len(pot_teams):
                        with cols[col_idx]:
                            self.st_display_team(
                                pot_teams[team_idx]['id'],
                                size='small',
                                available=pot_teams[team_idx]['id'] in available_team_ids
                            )

    def display_group_column(self, col):
        """Display current group status"""
        with col:
            if st.session_state['cur_team'] and st.session_state['draw_status'] not in ['drawing']:
                for group, team_ids in st.session_state['groups'].items():
                    if st.session_state['cur_team']['id'] in team_ids:
                        drawn_group = group
                        break
                # Show celebration image
                if st.session_state['draw_status'] in ['waiting_draw', 'waiting_next_pot', 'waiting_done']:
                    if st.session_state['cur_team']['name'] == 'FC Bayern München':
                        image_name = random.choice(self.MUELLER_IMAGES)
                    else:
                        image_name = random.choice(self.SIU_IMAGES)
                    st.image(f'static/{image_name}')
                # Show the drawn team's group
                st.write(f"**Group {drawn_group}**")
                self.display_single_group(drawn_group)
            else:
                image_name = random.choice(self.SAD_IMAGES)
                st.image(f'static/{image_name}') 

    def display_results(self):
        """Display all groups"""
        if st.session_state['draw_status'] == 'done':
            st.header('🏆 Final Groups')
        else:
            st.header('📺 Current Groups')
            
        # Display all groups in a vertical layout
        for group in self.groups:
            cols = st.columns([1, 6], vertical_alignment='center')
            with cols[0]:
                st.write(f"**Group {group}**")
            with cols[1]:
                self.display_single_group(group, rows=1)

    def display_single_group(self, group, rows=2):
        """Display a single group in a 2x2 grid"""
        group_teams = st.session_state['groups'][group]
        
        # Create a list of 4 slots (None represents empty slot)
        slots = [-1] * 4
        
        # Place teams in their designated positions
        for team_id in group_teams:
            team = self.teams_id_map[team_id]
            slots[team['pot'] - 1] = team_id
        
        if rows == 2:
            cols = 2
        elif rows == 1:
            cols = 4
        else:
            raise ValueError(f"Invalid number of rows: {rows}")

        for row in range(rows):
            columns = st.columns(cols)
            for col in range(cols):
                slot_idx = row * cols + col
                with columns[col]:
                    self.st_display_team(slots[slot_idx], size='small')


    def finish_draw(self):
        """Finish the draw process"""
        st.session_state['draw_status'] = 'done'
        st.balloons()

    def draw_next_pot(self):
        """Move to next pot"""
        st.session_state['current_pot'] += 1
        st.session_state['draw_status'] = 'waiting_draw'
        st.session_state['cur_team'] = None
