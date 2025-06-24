import xml.etree.ElementTree as ET
import re, os, sys
from A_episode_corrector import correct_episode_number

# Use the merged XML as base input/output, so repeated merges update same file
base_epg_path = 'Master_Location/Sydney_enhanced_EPG.xml'
enriched_file = sys.argv[1]  # Enriched file passed as argument

def extract_season_episode(text):
    # Improved regex to tolerate optional dots/spaces after "Ep"
    match = re.search(r'[Ss](\d+)\s*[Ee]p\.?\s*\.?\s*(\d+)', text)
    if match:
        season = int(match.group(1))
        episode = int(match.group(2))
        return season, episode
    return None, None

def build_enriched_map(path):
    lookup = {}
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        for prog in root.findall('programme'):
            channel = prog.get('channel')
            sub = prog.find('sub-title')
            if channel and sub is not None and sub.text:
                season, episode = extract_season_episode(sub.text)
                if season and episode:
                    episode = correct_episode_number(season, episode)
                    lookup[(channel, season, episode)] = prog
    except Exception as e:
        print(f"Failed parsing {path}: {e}")
    return lookup

def merge_metadata():
    # If merged base file doesn't exist yet, create it by copying original base EPG
    if not os.path.exists(base_epg_path):
        os.makedirs(os.path.dirname(base_epg_path), exist_ok=True)
        original_base = 'Backflow/Base_EPG_XML/base_syd.xml'
        import shutil
        shutil.copy2(original_base, base_epg_path)
    
    base_tree = ET.parse(base_epg_path)
    base_root = base_tree.getroot()
    enriched_map = build_enriched_map(enriched_file)

    for prog in base_root.findall('programme'):
        channel = prog.get('channel')
        title_el = prog.find('title')
        if title_el is None or not title_el.text:
            continue

        season, episode = extract_season_episode(title_el.text)
        if not season or not episode:
            continue

        episode = correct_episode_number(season, episode)
        enriched_prog = enriched_map.get((channel, season, episode))
        if not enriched_prog:
            continue

        # Preserve original attributes and title
        start = prog.get('start')
        stop = prog.get('stop')
        ch = prog.get('channel')
        title = prog.find('title')

        # Clear all children
        for tag in list(prog):
            prog.remove(tag)

        # Re-add original title
        prog.append(title)

        # Add enriched metadata (excluding title)
        for tag in enriched_prog:
            if tag.tag != 'title':
                prog.append(tag)

        # Restore original attributes
        prog.set('start', start)
        prog.set('stop', stop)
        prog.set('channel', ch)

    base_tree.write(base_epg_path, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    merge_metadata()
