import xml.etree.ElementTree as ET
import re, os, glob, sys
from A_episode_corrector import correct_episode_number, extract_season_episode

base_epg_path = 'Backflow/Base_EPG_XML/base_syd.xml'
enriched_dir = 'Backflow/Manual_Database'
output_path = 'Master_Location/Sydney_enhanced_EPG.xml'

def build_enriched_map():
    lookup = {}
    for path in glob.glob(f"{enriched_dir}/*.xml"):
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            for prog in root.findall('programme'):
                sub = prog.find('sub-title')
                if sub is not None and sub.text:
                    season, episode = extract_season_episode(sub.text)
                    if season and episode:
                        episode = correct_episode_number(season, episode)
                        lookup[(season, episode)] = prog
        except Exception as e:
            print(f"Failed parsing {path}: {e}")
    return lookup

def merge_metadata():
    base_tree = ET.parse(base_epg_path)
    base_root = base_tree.getroot()
    enriched_map = build_enriched_map()

    for prog in base_root.findall('programme'):
        title_el = prog.find('title')
        if title_el is None or not title_el.text:
            continue

        season, episode = extract_season_episode(title_el.text)
        if not season or not episode:
            continue

        episode = correct_episode_number(season, episode)
        enriched_prog = enriched_map.get((season, episode))
        if not enriched_prog:
            continue

        # Clear all tags except start/stop/channel
        for tag in list(prog):
            if tag.tag not in ('title',):
                prog.remove(tag)

        # Copy all enriched data except timing and channel
        for tag in enriched_prog:
            if tag.tag in ('start', 'stop', 'channel'):
                continue
            prog.append(tag)

    base_tree.write(output_path, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    merge_metadata()
