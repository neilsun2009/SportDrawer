from sport_drawer.base_drawer import BaseDrawer
import streamlit as st
import random
import copy


class WorldCupDrawer(BaseDrawer):
    
    tournament = 'FIFA World Cup 2026'
    highlight_color = 'rgba(193, 159, 87, 0.5)'
    
    def __init__(self, edition, teams_data_path, rules_url=None):
        self.groups = {chr(65+i): [] for i in range(12)}  # Groups A through L (12 groups)
        
        # Define pathways for Spain/Argentina and France/England constraints
        self.pathway1_groups = ['E', 'I', 'F', 'H', 'D', 'G']
        self.pathway2_groups = ['C', 'A', 'L', 'J', 'B', 'K']
        
        # Predetermined host teams (drawn but group is predetermined)
        self.predetermined_teams = {
            'Mexico': 'A',
            'Canada': 'B',
            'USA': 'D'
        }
        
        # Pathway pair constraints: these teams must be in opposite pathways
        self.pathway_pairs = {
            'Spain': 'Argentina',
            'Argentina': 'Spain',
            'France': 'England',
            'England': 'France'
        }
        
        # Celebration images
        self.COUNTRY_IMAGES = {
            "Mexico": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbjQ4cHVkc2FsNTh1MG1jdGcwdHNveXkzczZ5cmh5b3g5NGV2aTludSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/bOybLcXnijzW0/giphy.gif",
            "USA": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeGs5N3U4dXFtZ3VjOXU1cWx0b2J1d2V5Z3k0ZGZnOXhybTNteXRqNCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/FbiL9rsmZN3ib2JSGo/giphy.gif",
            "Canada": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNTFrYTVqdGY0NjFoMHZhbm5rNTZwY25zczliMHd3NzNnZDJsOXZpcyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3o6YgocGqX2pKCKxt6/giphy.gif",
            "Denmark": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYXIzZjczZXNwOHY5YmIzOWZnMTkxY2NjMTZqbXhjcDYwdGJud21pYyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/f7T8ozHCxRF06JJVxr/giphy.gif",
            "Germany": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3NiMGRqM2dmZzQ1Y3N6eTU0MThleGU5bms5bXBob2N6djAyeW4yOSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ddQyQAcXVXbLr6aLsr/giphy.gif",
            "Portugal": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNXpxM29iYXoxbG16amRrMmM4dzF3N3Rrb2N3YjhuejdtcmRienkzZCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/nfMNVc0Gb9PhXqcTZT/giphy.gif",
            "Argentina": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGNudDhna2dmdHQ2djdqY3piZmF0a25yYWt1enY1YXpwbWszZG90eSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/WzR8zb0PN6bUmfz4DW/giphy.gif",
            "Saudi Arabia": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3cGJjbjQ1ZjFsbTAxMmsxcDEyc2xvemNoNGFkaGR1OGpqNmVrOWxhYyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/PQvrUM9Z8FDdN2ne9X/giphy.gif",
            "Iran": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjVsZXk0ZWtqYXhudjFjdHpmbjJkYmRocXlobjNiZmx6bXNmazVkZCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/j0eo5xgTJ9ZF6ozCMx/giphy.gif",
            "Japan": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdzlkeGdnb2FiZnFxMHFnbDlpcHhtZHAyN2xkdW1oZmxvOTYwOTNlZiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/l0Exu3CpGQeycAO1q/giphy.gif",
        }
        self.DEFAULT_IMAGES = [
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3N2V1cXgxOWlhajhiNjRuMTN3emttaTRvOHNoNGZiMmtnYWc5YWJhOSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/u1ysISFV3VwPJUIqQW/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYXIzZjczZXNwOHY5YmIzOWZnMTkxY2NjMTZqbXhjcDYwdGJud21pYyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/l0HefZY0mFfLS9AFa/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3NjVzNmppMGsxaDB0MHB2ZHZuaDZldjlrMXg4MXBheGRpZWg0dHM0YyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/S43RIQ4OtWGKMTyU8q/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHYxbzhhMDlrY2JwdzczNDQ0YjNmZng1bnUwYzVoeGIxbjQ1ZW9icSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/fRtK3t3i67tRK4dfez/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeHU4ZHBuNm1hcTBjYTR5MmxhbHg4YXp6MWFtdWc4bnZxazhhaXJwNyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ELxTc8j0ixJGbXqTkR/giphy.gif",
        ]
        self.SAD_IMAGES = [
            'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3NocGFybXI5dWxya2YydjYwdmxjNzl0czRvZDRxNWg2a3VyNzltNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xTiTnHXbRoaZ1B1Mo8/giphy.gif',
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbnU5c3dtYXgxMWV4d211ejJnampseHIycWx2dTlheXJlaG14ZGY0cCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/l3vR3EssQ5ALagr7y/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3Z2tveXJpdjcxMzk3czhhbmIyYXpoN2lkbW11NmVkeTM1anJpdzMxeiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/lld3dQeRfolZwPyj7H/giphy.gif",
        ]
        
        super().__init__(edition, teams_data_path, rules_url)
        
    def init_custom_session(self):
        """Initialize World Cup-specific session variables"""
        st.session_state['current_pot'] = 1
        st.session_state['groups'] = {chr(65+i): [] for i in range(12)}  # Groups A through L
        st.session_state['selecting_logs'] = []
        st.session_state['pathway_allocations'] = {}  # Track Spain/Argentina and France/England
        
        # Initialize possible groups cache for each team (all groups initially)
        st.session_state['team_possible_groups'] = {
            team['id']: set(self.groups.keys()) for team in self.teams_data
        }
        
        # For predetermined teams, restrict their possible groups
        for team in self.teams_data:
            if team['name'] in self.predetermined_teams:
                predetermined_group = self.predetermined_teams[team['name']]
                st.session_state['team_possible_groups'][team['id']] = {predetermined_group}
    
    def get_confed_allocation_state(self):
        """Get current state of confederation allocations in groups"""
        state = {group: {
            'UEFA': [], 'CONMEBOL': [], 'AFC': [], 
            'CAF': [], 'CONCACAF': [], 'OFC': []
        } for group in self.groups}
        
        for group, team_ids in st.session_state['groups'].items():
            for team_id in team_ids:
                team = self.teams_id_map[team_id]
                # Handle playoff teams with multiple confederations
                if team.get('is_playoff'):
                    # For playoff teams, we'll track all possible confederations
                    for confed in team.get('confeds', []):
                        state[group][confed].append(team)
                else:
                    state[group][team['confed']].append(team)
                
        return state
    
    def can_join_group(self, team, group, allocation_state):
        """Check if a team can join a group based on World Cup constraints"""
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
        
        # Get the team's confederation(s)
        team_confeds = team.get('confeds', []) if team.get('is_playoff') else [team['confed']]
        
        # Check confederation constraints for each possible confederation
        can_join = True
        for team_confed in team_confeds:
            if team_confed == 'UEFA':
                # UEFA teams: up to 2 per group
                uefa_count = len(allocation_state[group]['UEFA'])
                if uefa_count >= 2:
                    can_join = False
                    break
            else:
                # Other confederations: max 1 per group
                confed_count = len(allocation_state[group][team_confed])
                if confed_count >= 1:
                    can_join = False
                    break
        
        if not can_join:
            return False
        
        # Check if this would be the last team in the group (pot 4)
        if len(group_teams) == 3:
            # This is the last position, must ensure group has at least one UEFA team
            has_uefa = len(allocation_state[group]['UEFA']) > 0
            is_uefa = 'UEFA' in team_confeds
            if not has_uefa and not is_uefa:
                return False
        
        # Check pathway constraints: pairs must be in opposite pathways
        if team['name'] in self.pathway_pairs:
            partner_name = self.pathway_pairs[team['name']]
            if partner_name in st.session_state.get('pathway_allocations', {}):
                partner_pathway = st.session_state['pathway_allocations'][partner_name]
                # If partner is in pathway 1, this team must be in pathway 2, and vice versa
                if (partner_pathway == 1 and group in self.pathway1_groups) or \
                   (partner_pathway == 2 and group in self.pathway2_groups):
                    return False
        
        return True
    
    def check_possible_allocation(self, team, confed_state, group, drawn_team_ids, simulated_possible_groups=None):
        """Check if allocating team to this group leads to a valid solution
        
        Uses a simulated copy of team_possible_groups to trim search space during recursion.
        """
        # print(f"Checking allocation of {team['name']} to Group {group}")
        # print(f"drawn_team_ids: {drawn_team_ids}")
        # print current drawn team with group
        
        # On first call, create a deep copy of team_possible_groups for simulation
        if simulated_possible_groups is None:
            simulated_possible_groups = copy.deepcopy(st.session_state['team_possible_groups'])
        
        simulated_possible_groups = copy.deepcopy(simulated_possible_groups)
        
        # Create new state with this allocation
        new_state = copy.deepcopy(confed_state)
        # Add team to the new state
        if team.get('is_playoff'):
            for confed in team.get('confeds', []):
                new_state[group][confed].append(team)
        else:
            new_state[group][team['confed']].append(team)
        
        group_team_ids = {}
        for state_group in new_state.keys():
            team_ids = []
            for confed in new_state[state_group].keys():
                team_ids.extend([team['id'] for team in new_state[state_group][confed]])
            group_team_ids[state_group] = team_ids
        # print(f"Group team ids: {group_team_ids}")
        
        # Simulate updating possible groups for this allocation
        simulated_possible_groups[team['id']] = {group}
        # print(f"simulated possible groups: {simulated_possible_groups}")
        
        # Update simulated possible groups for all undrawn teams
        for t in self.teams_data:
            if t['id'] in drawn_team_ids:
                continue
            
            possible = simulated_possible_groups[t['id']].copy()
            for g in possible:
                # Remove groups that are full (simulated)
                if len(group_team_ids.get(g, [])) >= 4:
                    simulated_possible_groups[t['id']].discard(g)
                # Remove same pot same group
                elif t['pot'] == team['pot'] and g == group:
                    simulated_possible_groups[t['id']].discard(g)
                # Remove groups that violate immediate constraints
                elif not self.can_join_group(t, g, new_state):
                    simulated_possible_groups[t['id']].discard(g)
            if len(simulated_possible_groups[t['id']]) == 0:
                return False
        
        
        # Find next team to process
        next_team_id = -1
        for t in self.teams_data:
            if t['id'] not in drawn_team_ids:
                next_team_id = t['id']
                break
        
        if next_team_id == -1:
            return True
        
        # Check if next team has any possible groups left
        next_team = self.teams_id_map[next_team_id]
        possible_groups = simulated_possible_groups[next_team_id]
        # print(f"Possible groups for {next_team['name']}: {possible_groups}")
        
        if len(possible_groups) == 0:
            return False
        
        # Try each possible group for the next team
        for next_group in sorted(possible_groups):
            if self.check_possible_allocation(
                next_team,
                new_state,
                next_group,
                drawn_team_ids + [next_team_id],
                simulated_possible_groups
            ):
                return True
        return False
    
    def update_possible_groups(self, drawn_team_id, allocated_group):
        """Update cached possible groups for all remaining teams after a team is drawn"""
        # Set the drawn team's possible groups to only the allocated group
        drawn_team = self.teams_id_map[drawn_team_id]
        st.session_state['team_possible_groups'][drawn_team_id] = {allocated_group}
        
        confed_state = self.get_confed_allocation_state()
        
        # Update possible groups for all undrawn teams
        for team in self.teams_data:
            if team['id'] in st.session_state['drawn_team_ids']:
                continue
                
            # Check each group that was previously possible
            possible_groups = st.session_state['team_possible_groups'][team['id']].copy()
            for group in possible_groups:
                if team['pot'] == drawn_team['pot'] and group == allocated_group:
                    st.session_state['team_possible_groups'][team['id']].discard(group)
                    
                # Remove groups that are no longer valid
                if len(st.session_state['groups'][group]) >= 4:
                    # Group is full
                    st.session_state['team_possible_groups'][team['id']].discard(group)
                elif not self.can_join_group(team, group, confed_state):
                    # Team can't join this group due to constraints
                    st.session_state['team_possible_groups'][team['id']].discard(group)
    
    def get_available_group(self, team):
        """Get available groups for a team based on constraints"""
        confed_state = self.get_confed_allocation_state()
        
        # Use cached possible groups instead of checking all groups
        possible_groups = st.session_state['team_possible_groups'][team['id']]
        
        # Check each possible group
        for group in sorted(possible_groups):
            if len(st.session_state['groups'][group]) < 4 and self.can_join_group(team, group, confed_state):
                # For each candidate group, verify that choosing it won't lead to a deadend
                if self.check_possible_allocation(team, confed_state, group, st.session_state['drawn_team_ids']):
                    return group
                    
        return None
    

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
        
        # Check if we need to draw predetermined teams first (in order: Mexico, Canada, USA)
        predetermined_order = ['Mexico', 'Canada', 'USA']
        drawn_team_id = None
        for predetermined_name in predetermined_order:
            for team_id in available_team_ids:
                if self.teams_id_map[team_id]['name'] == predetermined_name:
                    drawn_team_id = team_id
                    break
            if drawn_team_id is not None:
                break
        
        # If no predetermined team, draw randomly
        if drawn_team_id is None:
            drawn_team_id = random.choice(available_team_ids)
        
        drawn_team = self.teams_id_map[drawn_team_id]
        
        st.session_state['drawn_team_ids'].append(drawn_team_id)
        st.session_state['cur_team'] = drawn_team
        
        # Check if this is a predetermined team
        is_predetermined = drawn_team['name'] in self.predetermined_teams
        
        if is_predetermined:
            # Predetermined group
            group = self.predetermined_teams[drawn_team['name']]
        else:
            # Automatically assign to first available group (alphabetically)
            group = self.get_available_group(drawn_team)
            if not group:
                raise Exception(f"No valid group found for {drawn_team['name']}!")
            
        st.session_state['groups'][group].append(drawn_team_id)
        # print("--------------------------------")
        # print(f"Drawn {drawn_team['name']} to Group {group}")
        
        # Track pathway allocations for teams with pathway pair constraints
        if drawn_team['name'] in self.pathway_pairs:
            if group in self.pathway1_groups:
                st.session_state['pathway_allocations'][drawn_team['name']] = 1
            else:
                st.session_state['pathway_allocations'][drawn_team['name']] = 2
        
        # Update possible groups cache for remaining teams
        self.update_possible_groups(drawn_team_id, group)
        # print(f"Possible groups for {drawn_team['name']}: {st.session_state['team_possible_groups'][drawn_team_id]}")
        # print(st.session_state['team_possible_groups'])
        
        # Calculate how many teams have been drawn in current pot
        cur_pot_drawn_count = len([
            t for t in st.session_state['drawn_team_ids'] 
            if self.teams_id_map[t]['pot'] == cur_pot 
        ])
        
        st.toast(f"{drawn_team['name']} drawn to Group {group}!", icon='🎉')
        
        # Check if pot is complete (12 teams per pot)
        if cur_pot_drawn_count == 12:
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
                # Display in rows of 4
                num_rows = (len(pot_teams) + 3) // 4
                for row_idx in range(num_rows):
                    cols = st.columns(4)
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
        
        # Calculate current team number in pot
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
                    and len(available_team_ids) < 12:
                st.write(f"**{st.session_state['cur_team']['name']}** is drawn...")
                self.st_display_team(st.session_state['cur_team']['id'], highlight=True)
                
            st.write(f'**Teams from Pot {cur_pot}:**')
            # Display teams from current pot in 3 columns
            num_rows = (len(pot_teams) + 2) // 3
            for row_idx in range(num_rows):
                cols = st.columns(3)
                for col_idx in range(3):
                    team_idx = row_idx * 3 + col_idx
                    if team_idx < len(pot_teams):
                        with cols[col_idx]:
                            self.st_display_team(
                                pot_teams[team_idx]['id'],
                                size='small',
                                available=pot_teams[team_idx]['id'] in available_team_ids,
                                show_flag_only=True
                            )

    def display_group_column(self, col):
        """Display current group status"""
        with col:
            if st.session_state['cur_team'] and st.session_state['draw_status'] not in ['drawing']:
                for group, team_ids in st.session_state['groups'].items():
                    if st.session_state['cur_team']['id'] in team_ids:
                        drawn_group = group
                        break
                
                # Show the drawn team's group
                st.write(f"to **Group {drawn_group}**")
                self.display_single_group(drawn_group, highlight_ids=[st.session_state['cur_team']['id']])
                
                
                # Determine if we should show sad image
                is_predetermined = st.session_state['cur_team']['name'] in self.predetermined_teams
                
                # Check if this was the last team in the pot
                cur_pot = st.session_state['current_pot']
                cur_pot_drawn_count = len([
                    t for t in st.session_state['drawn_team_ids'] 
                    if self.teams_id_map[t]['pot'] == cur_pot 
                ])
                is_last_in_pot = cur_pot_drawn_count == 12
                
                # Show celebration or sad image
                if st.session_state['draw_status'] in ['waiting_draw', 'waiting_next_pot', 'waiting_done']:
                    country = st.session_state['cur_team']['name']
                    if country in self.COUNTRY_IMAGES:
                        image_url = self.COUNTRY_IMAGES[country]
                    elif is_predetermined or is_last_in_pot:
                        image_url = random.choice(self.SAD_IMAGES)
                    else:
                        image_url = random.choice(self.DEFAULT_IMAGES)
                    st.image(image_url)
                
                
            else:
                image_url = random.choice(self.SAD_IMAGES)
                st.image(image_url) 

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
                self.display_single_group(group, rows=1, 
                                          highlight_ids=[st.session_state['cur_team']['id']] if st.session_state['cur_team'] else None)

    def display_single_group(self, group, rows=2, highlight_ids=None):
        """Display a single group"""
        group_teams = st.session_state['groups'][group]
        
        # Create a list of 4 slots (None represents empty slot)
        slots = [-1] * 4
        
        # Place teams in their designated positions (by pot)
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
                highlight = slots[slot_idx] in highlight_ids if highlight_ids else False
                with columns[col]:
                    self.st_display_team(slots[slot_idx], size='small', show_flag_only=True, 
                                         highlight=highlight)

    def finish_draw(self):
        """Finish the draw process"""
        st.session_state['draw_status'] = 'done'
        st.session_state['cur_team'] = None
        st.balloons()

    def draw_next_pot(self):
        """Move to next pot"""
        st.session_state['current_pot'] += 1
        st.session_state['draw_status'] = 'waiting_draw'
        st.session_state['cur_team'] = None 