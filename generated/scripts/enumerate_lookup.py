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
            list(emily_symbols.symbols[starter]) == [""]
            and emily_symbols.symbols[starter][""] == "test"
        ):
            continue

        for attachment in ["", "A", "O", "AO"]:
            for capitalization in "*-":
                for variant in ["", "E", "U", "EU"]:
                    # hyphen should be removed when AOEU are around
                    # example: SKWHA-FP
                    if capitalization == "-" and (attachment or variant):
                        capitalization = ""

                    for pattern in patterns:
                        for repititions in ["", "S", "T", "TS"]:
                            yield f"{starter}{attachment}{'' if not (pattern or repititions) else capitalization}{variant}{pattern}{repititions}"


key_to_number = str.maketrans(
    {
        "S": "1",
        "T": "2",
        # "P": "3",
        "H": "4",
        "A": "5",
        "O": "0",
        "F": "6",
        # "P": "7",
        "L": "8",
        "T": "9",
    }
)

# steno_order = "#STKPWHRAO*EUFRPBLGTSDZ"


def embed_numbers(outline: str) -> str:
    "embeds numbers in an outline beginning with #"
    if "#" not in outline:
        return outline

    if "P" not in outline:
        return outline.translate(key_to_number)

    elif outline.count("P") == 2:
        return outline.translate(key_to_number).replace("P", "3", 1).replace("P", "7")

    elif outline.count("P") == 1:
        left, _, right = outline.partition("P")
        if any(key in left for key in set("WHRAO*-EUFR")):
            # right-hand P
            return outline.translate(key_to_number).replace("P", "7")
        
        return outline.translate(key_to_number).replace("P", "3")

    else:
        raise ValueError(f"too many 'P's in outline '{outline}'")


if __name__ == "__main__":
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
    Path("emily-symbols-attachment.json").write_text(
        json.dumps(attachment_dictionary, indent=2)
    )
