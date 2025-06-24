import xml.etree.ElementTree as ET
import re
import glob
import os
import sys

# Include episode corrector logic from sibling script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from A_episode_corrector import correct_episode_number

# Paths
base_epg_path = 'Backflow/scripts/Base_syd.xml'
enriched_dir = 'Backflow/Manual_Database'
output_path = 'Master_Location/Sydney_enhanced_EPG.xml'

def extract_season_episode(text):
    if not text:
        return None, None
    match = re.search(r"S(\d+)\s*Ep\.?\s*(\d+)", text, re.IGNORECASE)
    if not match:
        return None, None
    season = int(match.group(1))
    episode = int(match.group(2))
    return season, episode

def build_enriched_map():
    lookup = {}
    for path in glob.glob(f"{enriched_dir}/*.xml"):
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
    base_tree = ET.parse(base_epg_path)
    base_root = base_tree.getroot()
    enriched_map = build_enriched_map()

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
        if enriched_prog is None:
            continue

        # Remove old enrichment tags
        for tag in ['sub-title', 'desc', 'category', 'icon', 'rating', 'date']:
            for el in prog.findall(tag):
                prog.remove(el)

        # Copy enrichment tags
        for tag in ['sub-title', 'desc', 'icon', 'rating', 'date']:
            el = enriched_prog.find(tag)
            if el is not None:
                new_el = ET.Element(tag, el.attrib)
                new_el.text = el.text
                prog.append(new_el)

        # Copy category tags separately
        for cat in enriched_prog.findall('category'):
            new_cat = ET.Element('category', cat.attrib)
            new_cat.text = cat.text
            prog.append(new_cat)

    base_tree.write(output_path, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    merge_metadata()
