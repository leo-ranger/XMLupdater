import sys
import re
import xml.etree.ElementTree as ET
from typing import Tuple

def correct_episode_number(season: int, episode: int) -> int:
    ep_str = str(episode)
    season_str = str(season)
    if season >= 10 and ep_str.startswith(season_str):
        fixed_str = ep_str[len(season_str):].lstrip('0')
        if fixed_str.isdigit() and len(fixed_str) > 0:
            return int(fixed_str)
    return episode

def extract_season_episode(text: str) -> Tuple[int, int]:
    if not text:
        return None, None
    match = re.search(r"S(\d+)\s*Ep\.?\s*(\d+)", text, re.IGNORECASE)
    if not match:
        return None, None
    season = int(match.group(1))
    episode = int(match.group(2))
    return season, episode

def correct_epg_episodes(file_path: str):
    tree = ET.parse(file_path)
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
            new_title = re.sub(
                r"(S\d+\s*Ep\.?\s*)\d+",
                r"\1{}".format(corrected_episode),
                title_el.text,
                flags=re.IGNORECASE
            )
            title_el.text = new_title

    tree.write(file_path, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python A_episode_corrector.py <input_xml>")
        sys.exit(1)
    input_file = sys.argv[1]
    correct_epg_episodes(input_file)
