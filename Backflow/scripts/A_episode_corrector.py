import re
import xml.etree.ElementTree as ET

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

def extract_season_episode(text: str):
    """
    Extracts season and episode numbers from text like 'S12 Ep23'.
    Returns (season:int, episode:int) or (None, None) if no match.
    """
    if not text:
        return None, None
    match = re.search(r"S(\d+)\s*Ep\.?\s*(\d+)", text, re.IGNORECASE)
    if not match:
        return None, None
    season = int(match.group(1))
    episode = int(match.group(2))
    return season, episode

def correct_tree_episodes(tree: ET.ElementTree):
    """
    Modifies the given XML tree in-place.
    Finds all <programme> elements and corrects episode numbers in <title> tags if needed.
    """
    root = tree.getroot()
    for prog in root.findall('programme'):
        title_el = prog.find('title')
        if title_el is None or not title_el.text:
            continue
        season, episode = extract_season_episode(title_el.text)
        if season is None or episode is None:
            continue

        corrected_ep = correct_episode_number(season, episode)
        if corrected_ep != episode:
            # Replace episode number in title text preserving format
            # Example: "South Park S12 Ep1223" → "South Park S12 Ep23"
            new_title = re.sub(r"(S\d+\s*Ep\.?)(\d+)", rf"\1{corrected_ep}", title_el.text, flags=re.IGNORECASE)
            title_el.text = new_title
