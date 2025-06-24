import xml.etree.ElementTree as ET
import re
import sys

def correct_episode_number(season: int, episode: int) -> int:
    ep_str = str(episode)
    season_str = str(season)
    if season >= 10 and ep_str.startswith(season_str):
        fixed_str = ep_str[len(season_str):].lstrip('0')
        if fixed_str.isdigit() and len(fixed_str) > 0:
            return int(fixed_str)
    return episode

def extract_season_episode(text):
    if not text:
        return None, None
    match = re.search(r"S(\d+)\s*Ep\.?\s*(\d+)", text, re.IGNORECASE)
    if not match:
        return None, None
    season = int(match.group(1))
    episode = int(match.group(2))
    episode = correct_episode_number(season, episode)
    return season, episode

def correct_episodes_in_file(input_path, output_path):
    tree = ET.parse(input_path)
    root = tree.getroot()
    for prog in root.findall('programme'):
        title_el = prog.find('title')
        if title_el is not None and title_el.text:
            season, episode = extract_season_episode(title_el.text)
            if season and episode:
                corrected_episode = correct_episode_number(season, episode)
                # If corrected episode differs, fix title text accordingly
                if corrected_episode != episode:
                    # Replace episode number in title text
                    new_title = re.sub(r"(S\d+\s*Ep\.?\s*)\d+", f"\\1{corrected_episode}", title_el.text, flags=re.IGNORECASE)
                    title_el.text = new_title
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python A_episode_corrector.py input.xml output.xml")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    correct_episodes_in_file(input_path, output_path)
