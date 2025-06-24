import xml.etree.ElementTree as ET
import requests
import time

file_path = "Backflow/offline/episodes/The_Golden_Girls.xml"
tvmaze_show_id = 530  # TVmaze ID for "The Golden Girls"

episode_cache = {}

def get_episode_name(season, episode):
    key = f"S{season:02d}E{episode:02d}"
    if key in episode_cache:
        return episode_cache[key]
    url = f"https://api.tvmaze.com/shows/{tvmaze_show_id}/episodebynumber?season={season}&number={episode}"
    response = requests.get(url)
    if response.status_code == 200:
        title = response.json().get("name", "")
        episode_cache[key] = title
        return title
    return ""

tree = ET.parse(file_path)
root = tree.getroot()

for programme in root.findall("programme"):
    ep_tag = programme.find("./episode-num[@system='SxxExx']")
    if ep_tag is None or not ep_tag.text:
        continue
    epcode = ep_tag.text.strip()
    match = epcode.upper().replace("S", "").split("E")
    if len(match) != 2:
        continue
    try:
        season = int(match[0])
        episode = int(match[1])
    except ValueError:
        continue
    episode_name = get_episode_name(season, episode)
    if not episode_name:
        continue
    subtitle_text = f"{episode_name} – {epcode}"
    title_tag = programme.find("title")
    if title_tag is not None:
        subtitle_tag = ET.Element("sub-title")
        subtitle_tag.text = subtitle_text
        title_index = list(programme).index(title_tag)
        programme.insert(title_index + 1, subtitle_tag)
    time.sleep(0.2)

tree.write(file_path, encoding="utf-8", xml_declaration=True)
