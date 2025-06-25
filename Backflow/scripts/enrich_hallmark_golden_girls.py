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

# Prepare a list of changes (but don’t apply yet)
programmes_to_replace = []
unmatched = 0

for programme in input_root.findall("programme"):
    title = programme.findtext("title", "").strip()
    if title != "The Golden Girls":
        continue
    input_desc = programme.findtext("desc", "").strip()
    if not input_desc:
        unmatched += 1
        continue

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
        replacement = copy_programme_with_time_attrs(best_match, original_attrs)
        programmes_to_replace.append((programme, replacement))
    else:
        unmatched += 1

# SAFETY: If there are any unmatched, cancel all changes
if unmatched > 0:
    print(f"❌ {unmatched} unmatched Golden Girls episodes. No changes applied.")
else:
    for old_prog, new_prog in programmes_to_replace:
        input_root.remove(old_prog)
        input_root.append(new_prog)
    input_tree.write(input_path, encoding="utf-8", xml_declaration=True)
    print(f"✅ Replaced {len(programmes_to_replace)} Golden Girls episodes.")
