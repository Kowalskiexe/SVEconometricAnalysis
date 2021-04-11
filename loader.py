import yaml
from player import Player
import pandas as pd


config_path = './config'

def load_player() -> Player:
    with open(f'{config_path}/player.yml') as file:
        print('loading player info')
        doc = yaml.full_load(file)
        player = Player(doc['energy'],
                        doc['wateringCost'],
                        doc['alreadyTaken'],
                        doc['seedCapital'],
                        doc['profession'],
                        doc['season'],
                        doc['dayOfSeason'])
        print('player info loaded\n')
    return player

def load_crop_types() -> pd.DataFrame:
    return pd.read_csv(f'{config_path}/crop_types.csv')
