from sport_drawer.base_drawer import BaseDrawer

class ClubWorldCupDrawer(BaseDrawer):
    def __init__(self, edition, teams_data_path, rules_url):
        super().__init__(edition, teams_data_path, rules_url)
