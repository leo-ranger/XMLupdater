import xml.etree.ElementTree as ET
import re, glob

base_epg_path = 'Backflow/base_au_epg.xml'
enriched_dir = 'Backflow/Manual_Database'
output_path = 'Master_Location/Enhanced_sydney_epg.xml'

def extract_season_episode(text):
    if not text:
        return None, None
    match = re.search(r"S(\d+)\s*Ep\.?\s*(\d+)", text, re.IGNORECASE)
    if not match:
        return None, None
    return int(match.group(1)), int(match.group(2))

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

        enriched_prog = enriched_map.get((channel, season, episode))
        if not enriched_prog:
            continue

        # Remove old enrichment tags
        for tag in ['sub-title', 'desc', 'category', 'icon', 'rating', 'date']:
            for el in prog.findall(tag):
                prog.remove(el)

        # Copy enrichment tags from enriched_prog
        for tag in ['sub-title', 'desc', 'icon', 'rating', 'date']:
            el = enriched_prog.find(tag)
            if el is not None:
                new_el = ET.Element(tag, el.attrib)
                new_el.text = el.text
                prog.append(new_el)

        # Copy all <category> tags
        for cat in enriched_prog.findall('category'):
            new_cat = ET.Element('category', cat.attrib)
            new_cat.text = cat.text
            prog.append(new_cat)

    base_tree.write(output_path, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    merge_metadata()
