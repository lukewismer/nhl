import requests, bs4

def web_scrape_advanced_stats(player_id):
    # Returns all advanced stats from given player
    
    try:
        # see if player_id has a valid url
        data = requests.get(f'https://www.naturalstattrick.com/playerreport.php?fromseason=20212022&thruseason=20212022&playerid={player_id}&sit=5v5&stype=2')
    except:
        print(f'{player_id} does not exist')
    else:

        # Beautiful soup webscraper
        soup = bs4.BeautifulSoup(data.content, 'lxml')

        # Gets list of all the rows in the table
        num_rows = soup.select("#indreg > tbody > tr")

        advanced_stats = {}

        # Detects how many rows pop up for each table
        key = len(num_rows)
        
        if soup.select(f'#indreg > tbody > tr') != []:
            # Individual Advanced Stats (table 1)
            advanced_stats['first_assists'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(7)')[0].text
            advanced_stats['second_assists'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(8)')[0].text
            advanced_stats['IPP'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(10)')[0].text
            advanced_stats['individual_expected_goals'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(13)')[0].text
            advanced_stats['individual_corsi_for'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(14)')[0].text
            advanced_stats['individual_fenwick_for'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(15)')[0].text
            advanced_stats['individual_scoring_chance_for'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(16)')[0].text
            advanced_stats['individual_high_danger_chance_for'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(17)')[0].text
            advanced_stats['rebounds_created'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(18)')[0].text
            advanced_stats['penalties_drawn'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(24)')[0].text
            advanced_stats['giveaways'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(25)')[0].text
            advanced_stats['takeaways'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(26)')[0].text
            advanced_stats['hits_taken'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(28)')[0].text
            advanced_stats['faceoffs_won'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(30)')[0].text
            advanced_stats['faceoffs_lost'] = soup.select(f'#indreg > tbody > tr:nth-child({key}) > td:nth-child(31)')[0].text

        if soup.select(f'#reg > tbody > tr') != []:
            # Advanced Stats Player was on Ice for (table 2)
            advanced_stats['corsi_for'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(5)')[0].text
            advanced_stats['corsi_against'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(6)')[0].text
            advanced_stats['corsi_for_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(7)')[0].text
            advanced_stats['fenwick_for'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(8)')[0].text
            advanced_stats['fenwick_against'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(9)')[0].text
            advanced_stats['fenwick_for_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(10)')[0].text
            advanced_stats['shots_for'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(11)')[0].text
            advanced_stats['shots_against'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(12)')[0].text
            advanced_stats['shots_for_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(13)')[0].text
            advanced_stats['goals_for'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(14)')[0].text
            advanced_stats['goals_against'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(15)')[0].text
            advanced_stats['goals_for_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(16)')[0].text
            advanced_stats['expected_goals_for'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(17)')[0].text
            advanced_stats['expected_goals_against'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(18)')[0].text
            advanced_stats['expected_goals_for_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(19)')[0].text
            advanced_stats['scoring_chance_for'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(20)')[0].text
            advanced_stats['scoring_chance_against'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(21)')[0].text
            advanced_stats['scoring_chance_for_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(22)')[0].text
            advanced_stats['high_danger_chance_for'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(23)')[0].text
            advanced_stats['high_danger_chance_against'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(24)')[0].text
            advanced_stats['high_danger_chance_for_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(25)')[0].text
            advanced_stats['high_danger_goals_for'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(26)')[0].text
            advanced_stats['high_danger_goals_against'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(27)')[0].text
            advanced_stats['high_danger_goals_for_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(28)')[0].text
            advanced_stats['mid_danger_chance_for'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(29)')[0].text
            advanced_stats['mid_danger_chance_against'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(30)')[0].text
            advanced_stats['mid_danger_chance_for_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(31)')[0].text
            advanced_stats['mid_danger_goals_for'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(32)')[0].text
            advanced_stats['mid_danger_goals_against'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(33)')[0].text
            advanced_stats['mid_danger_goals_for_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(34)')[0].text
            advanced_stats['low_danger_chance_for'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(35)')[0].text
            advanced_stats['low_danger_chance_against'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(36)')[0].text
            advanced_stats['low_danger_chance_for_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(37)')[0].text
            advanced_stats['low_danger_goals_for'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(38)')[0].text
            advanced_stats['low_danger_goals_against'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(39)')[0].text
            advanced_stats['low_danger_goals_for_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(40)')[0].text
            advanced_stats['on_ice_shot_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(41)')[0].text
            advanced_stats['on_ice_save_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(42)')[0].text
            advanced_stats['PDO'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(43)')[0].text
            advanced_stats['offensive_zone_starts'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(44)')[0].text
            advanced_stats['neutral_zone_starts'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(45)')[0].text
            advanced_stats['defensive_zone_starts'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(46)')[0].text
            advanced_stats['on_fly_starts'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(47)')[0].text
            advanced_stats['offensive_zone_start_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(48)')[0].text
            advanced_stats['offensive_zone_faceoffs'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(49)')[0].text
            advanced_stats['neutral_zone_faceoffs'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(50)')[0].text
            advanced_stats['defensive_zone_faceoffs'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(51)')[0].text
            advanced_stats['offensive_zone_faceoffs_percent'] = soup.select(f'#reg > tbody > tr:nth-child({key}) > td:nth-child(52)')[0].text

        return advanced_stats