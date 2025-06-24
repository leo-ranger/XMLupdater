import xml.etree.ElementTree as ET
import requests, time, re, os
import sys

# Add parent directory (Backflow/scripts) to sys.path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from A_episode_corrector import correct_episode_number

TVMAZE_SHOW_ID = 112
INPUT_XML = sys.argv[1]
OUTPUT_XML = sys.argv[1]  # or you can allow separate output if you want
FIXED_ICON = "https://tendaily-prod-images.s3.ap-southeast-2.amazonaws.com/2020/09/18/9af150a4ebd91350a4713fa737952a1d-993431.jpg"
TRAKT_CLIENT_ID = os.environ['TRAKT_CLIENT_ID']

def get_tvmaze_episode(season, episode):
    url = f"https://api.tvmaze.com/shows/{TVMAZE_SHOW_ID}/episodebynumber?season={season}&number={episode}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            time.sleep(1.5)
            return r.json()
    except Exception:
        pass
    time.sleep(1.5)
    return None

def get_trakt_episode(season, episode):
    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version': '2',
        'trakt-api-key': TRAKT_CLIENT_ID
    }
    url = f"https://api.trakt.tv/shows/south-park/seasons/{season}/episodes/{episode}?extended=full"
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            time.sleep(1.5)
            return r.json()
    except Exception:
        pass
    time.sleep(1.5)
    return None

def safe_get_episode(season, episode):
    # We assume episode is already corrected at this point.
    # Validate it against TVmaze, fallback etc as before.

    if episode <= 20:
        return episode

    if get_tvmaze_episode(season, episode):
        return episode

    ep_str = str(episode)
    for i in range(1, 3):
        tail = ep_str[-i:]
        if tail.isdigit():
            tail_ep = int(tail)
            if get_tvmaze_episode(season, tail_ep):
                print(f"Fallback fix: S{season} Ep.{episode} → Ep.{tail_ep}")
                return tail_ep

    print(f"Unresolvable episode: S{season} Ep.{episode}")
    return None

def strip_html(text):
    return re.sub('<[^<]+?>', '', text or '')

def main():
    tree = ET.parse(INPUT_XML)
    root = tree.getroot()
    title_re = re.compile(r"South Park S(\d+) Ep\.? ?(\d+)", re.IGNORECASE)

    for prog in root.findall('programme'):
        prog.set('channel', 'mjh-10-south-park')

        title_el = prog.find('title')
        if title_el is None or not title_el.text:
            continue
        match = title_re.match(title_el.text.strip())
        if not match:
            continue

        season = int(match.group(1))
        episode = int(match.group(2))

        # Correct episode number here
        episode = correct_episode_number(season, episode)
        # Then validate/fallback
        episode = safe_get_episode(season, episode)
        if episode is None:
            continue

        ep_data = get_tvmaze_episode(season, episode)
        fallback = get_trakt_episode(season, episode) if not ep_data else None

        ep_name = ep_data.get('name') if ep_data else fallback.get('title') if fallback else 'Unknown Episode'
        genres = ep_data.get('genres') if ep_data else fallback.get('genres') if fallback else []
        summary = ep_data.get('summary') if ep_data else fallback.get('overview') if fallback else ''
        airdate = ep_data.get('airdate') if ep_data else fallback.get('first_aired') if fallback else None
        rating = fallback.get('rating', {}).get('value') if fallback and fallback.get('rating') else None

        title_el.text = "South Park"

        for tag in ['sub-title', 'category', 'desc', 'icon', 'rating', 'date']:
            for el in prog.findall(tag):
                prog.remove(el)

        ET.SubElement(prog, 'sub-title').text = f"{ep_name} - S{season} Ep. {episode}"

        for genre in set(genres or []) | {"Comedy", "Animation"}:
            cat = ET.SubElement(prog, 'category', {'lang': 'en'})
            cat.text = genre

        if summary:
            ET.SubElement(prog, 'desc').text = strip_html(summary)

        if airdate:
            ET.SubElement(prog, 'date').text = airdate[:10]

        if rating:
            r = ET.SubElement(prog, 'rating', {'system': 'Trakt'})
            r.text = f"{rating:.1f}"

        ET.SubElement(prog, 'icon', {'src': FIXED_ICON})

    tree.write(OUTPUT_XML, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    main()
