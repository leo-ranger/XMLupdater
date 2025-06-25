import xml.etree.ElementTree as ET
from rapidfuzz.fuzz import ratio

input_path = "individual/USA-Hallmark_EastUS.xml"
reference_path = "Backflow/offline/episodes/The_Golden_Girls.xml"

# Load both XML trees
input_tree = ET.parse(input_path)
input_root = input_tree.getroot()

ref_tree = ET.parse(reference_path)
ref_root = ref_tree.getroot()

# Index reference episodes by C-desc
ref_programmes = []
for programme in ref_root.findall("programme"):
    cdesc = programme.findtext("C-desc", "").strip()
    if cdesc:
        ref_programmes.append((cdesc, programme))

# Function to preserve channel/start/stop attributes
def copy_programme_with_time_attrs(source, original_attrs):
    new_prog = ET.Element("programme", attrib=original_attrs)
    for child in source:
        new_prog.append(child)
    return new_prog

# Track replacements
replaced = 0
unmatched = 0

# Iterate and replace matched episodes
for i, programme in enumerate(input_root.findall("programme")):
    title = programme.findtext("title", "").strip()
    if title != "The Golden Girls":
        continue

    input_desc = programme.findtext("desc", "").strip()
    if not input_desc:
        unmatched += 1
        continue

    # Find best fuzzy match
    best_match = None
    best_score = 0
    for cdesc, ref_prog in ref_programmes:
        score = ratio(input_desc, cdesc)
        if score > best_score:
            best_score = score
            best_match = ref_prog

    if best_score >= 85 and best_match is not None:
        original_attrs = {
            "channel": programme.attrib.get("channel", ""),
            "start": programme.attrib.get("start", ""),
            "stop": programme.attrib.get("stop", "")
        }
        new_prog = copy_programme_with_time_attrs(best_match, original_attrs)
        input_root.remove(programme)
        input_root.insert(i, new_prog)
        replaced += 1
    else:
        unmatched += 1

# Save updated XML
input_tree.write(input_path, encoding="utf-8", xml_declaration=True)

print(f"✅ Replaced {replaced} Golden Girls episodes.")
print(f"⚠️ Unmatched: {unmatched}")
