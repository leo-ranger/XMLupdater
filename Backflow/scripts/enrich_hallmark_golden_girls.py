import xml.etree.ElementTree as ET
from rapidfuzz.fuzz import ratio

input_path = "individual/USA-Hallmark_EastUS.xml"
reference_path = "Backflow/offline/episodes/The_Golden_Girls.xml"

# Load XML
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

# Util: Copy node while skipping <C-desc>
def copy_programme_with_time_attrs(source_prog, original_attrs):
    new_prog = ET.Element("programme", attrib=original_attrs)
    for child in source_prog:
        if child.tag == "C-desc":
            continue  # Exclude C-desc from replacement
        new_prog.append(child)
    return new_prog

# Perform replacements
replaced = 0
unmatched = 0

for i, programme in enumerate(input_root.findall("programme")):
    title = programme.findtext("title", "").strip()
    if title != "The Golden Girls":
        continue

    input_desc = programme.findtext("desc", "").strip()
    if not input_desc:
        unmatched += 1
        continue

    # Fuzzy match against C-desc
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

# Save changes
input_tree.write(input_path, encoding="utf-8", xml_declaration=True)

print(f"✅ Replaced {replaced} Golden Girls episodes.")
print(f"⚠️ Skipped {unmatched} unmatched episodes.")
