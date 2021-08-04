import json
from itertools import compress
from pathlib import Path

import emily_symbols

pattern_keys = "FRPBLG"
patterns = [
    "".join(compress(pattern_keys, map(int, f"{x:0{len(pattern_keys)}b}")))
    for x in range(2 ** len(pattern_keys))
]


def generate_combinations():
    # vary uniqueStarters
    for starter in emily_symbols.symbols:
        # detect no custom symbols
        if (
            emily_symbols.symbols[starter].keys() == [""]
            and emily_symbols.symbols[starter][""] == "test"
        ):
            continue

        for attachment in ["", "A", "O", "AO"]:
            for capitalization in "*-":
                for variant in ["", "E", "U", "EU"]:
                    for pattern in patterns:
                        for repititions in ["", "S", "T", "TS"]:
                            yield f"{starter}{attachment}{capitalization}{variant}{pattern}{repititions}"


space_dictionary = {}
attachment_dictionary = {}
for outline in generate_combinations():
    emily_symbols.attachmentMethod = "space"
    try:
        space_dictionary[outline] = emily_symbols.lookup((outline,))
    except KeyError:
        pass

    emily_symbols.attachmentMethod = "attachment"
    try:
        attachment_dictionary[outline] = emily_symbols.lookup((outline,))
    except KeyError:
        pass

Path("emily-symbols-space.json").write_text(json.dumps(space_dictionary, indent=2))
Path("emily-symbols-attachment.json").write_text(json.dumps(attachment_dictionary, indent=2))
