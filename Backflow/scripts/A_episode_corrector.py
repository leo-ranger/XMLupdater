import sys
import re
import xml.etree.ElementTree as ET
from typing import Tuple

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

def extract_season_episode(text: str) -> Tuple[int, int]:
    """
    Extract season and episode numbers from a string like 'S07 Ep07' or 'S10 Ep1010'
    """
    if not text:
        return None, None
    match = re.search(r"S(\d+)\s*Ep\.?\s*(\d+)", text, re.IGNORECASE)
    if not match:
        return None, None
    season = int(match.group(1))
    episode = int(match.group(2))
    return season, episode

def correct_epg_episodes(input_path: str, output_path: str):
    tree = ET.parse(input_path)
    root = tree.getroot()

    for prog in root.findall('programme'):
        title_el = prog.find('title')
        if title_el is None or not title_el.text:
            continue
        season, episode = extract_season_episode(title_el.text)
        if season is None or episode is None:
            continue
        
        corrected_episode = correct_episode_number(season, episode)
        if corrected_episode != episode:
            # Replace episode number in the title string
            # This preserves the original formatting except for the episode number.
            new_title = re.sub(
                r"(S\d+\s*Ep\.?\s*)\d+",
                r"\1{}".format(corrected_episode),
                title_el.text,
                flags=re.IGNORECASE
            )
            title_el.text = new_title

    tree.write(output_path, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python A_episode_corrector.py <input_xml> <output_xml>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    correct_epg_episodes(input_file, output_file)
