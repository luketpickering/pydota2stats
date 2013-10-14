num_retry = 5
api_key = 'CF1BFAC7594ADDC9AB69250477B20CCD'
matches_d_sum_url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/?game_mode=0&account_id=%s&date_max=%s&date_min=%s&key=%s'
match_details_url = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/?match_id=%s&key=%s'

#using the test API
#matches_d_sum_url = 'https://api.steampowered.com/IDOTA2Match_205790/GetMatchHistory/V001/?game_mode=0&account_id=%s&date_max=%s&date_min=%s&key=%s'
#match_details_url = 'https://api.steampowered.com/IDOTA2Match_205790/GetMatchDetails/V001/?match_id=%s&key=%s'

hero_data_url = 'https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?key=%s&language=en_us'
sql_con_str = 'sqlite:///dota2_stats.sqlite'
dummy_sid32 = 4294967295

get_heroes = False
add_user = False
new_user_name = "luke"
new_user_steamid64 = '76561197984725352'
new_user_steamid = int(new_user_steamid64) - 76561197960265728

init_db = False

account_id64 = '76561198011127175'
account_id32 = int(account_id64) - 76561197960265728
account_id = account_id32

account_id = new_user_steamid
