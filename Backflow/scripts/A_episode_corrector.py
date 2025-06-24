def correct_episode_number(season: int, episode: int) -> int:
    """
    Corrects episode number if it is mistakenly prefixed with season number.
    
    Examples:
    - Season 12, episode 1223 -> corrected to episode 23
    - Season 24, episode 2407 -> corrected to episode 7
    - If no correction needed, returns original episode.
    """
    ep_str = str(episode)
    season_str = str(season)
    
    # Only apply correction if season >= 10 and episode starts with season number
    if season >= 10 and ep_str.startswith(season_str):
        fixed_str = ep_str[len(season_str):].lstrip('0')  # strip leading zeros
        if fixed_str.isdigit() and len(fixed_str) > 0:
            corrected_episode = int(fixed_str)
            return corrected_episode
    
    return episode
