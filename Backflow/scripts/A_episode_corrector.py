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

def fix_episode_text(text):
    if not text:
        return text
    # Matches S7 Ep707, S07 Ep007, etc.
    pattern = re.compile(r"(S(\d+)\s*Ep\.?\s*)(\d+)", re.IGNORECASE)
    def repl(m):
        season_num = int(m.group(2))
        episode_num = int(m.group(3))
        corrected_ep = correct_episode_number(season_num, episode_num)
        return f"S{season_num} Ep{corrected_ep}"
    return pattern.sub(repl, text)

def correct_episodes_in_file(file_path, output_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    for prog in root.findall('programme'):
        # Correct <title>
        title = prog.find('title')
        if title is not None and title.text:
            title.text = fix_episode_text(title.text)
        # Correct <sub-title>
        sub_title = prog.find('sub-title')
        if sub_title is not None and sub_title.text:
            sub_title.text = fix_episode_text(sub_title.text)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python A_episode_corrector.py input.xml output.xml")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    correct_episodes_in_file(input_file, output_file)
