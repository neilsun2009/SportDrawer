import toml
import requests
import json
import os

SEASON = 2024
URL = f'https://api.football-data.org/v4/competitions/CL/teams?season={SEASON}'
SECRET_FILE = '../.streamlit/secrets.toml'
OUTPUT_FILE = f'../data/ucl_{SEASON}/teams-football-data.json'

def main():
    config = toml.load(SECRET_FILE)
    token = config['football_data_key']
    headers = {'X-Auth-Token': token}
    response = requests.get(URL, headers=headers)
    data = response.json()
    if not os.path.exists(os.path.dirname(OUTPUT_FILE)):
        os.makedirs(os.path.dirname(OUTPUT_FILE))
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
if __name__ == '__main__':
    main()