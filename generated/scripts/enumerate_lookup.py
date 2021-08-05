#!/usr/bin/env python
"""
generates json stenographic dictionaries of Emily's system for use with
openstenoproject/plover
"""
import argparse
import json
import sys
from itertools import compress
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from typing import Optional, Sequence, Iterator, List, Dict

import emily_symbols


class Outline(NamedTuple):
    starter: "str"
    attachment: "str"
    capitalization: "str"
    variant: "str"
    pattern: "str"
    repititions: "str"


def str_to_int(string: str) -> int:
    "makes mypy happy"
    if string.isdigit():
        return int(string)

    raise ValueError(f"not a number: {string}")


pattern_keys = "FRPBLG"
patterns: "List[str]" = []
for number in range(1 << len(pattern_keys)):
    # same as 2 ** len(pattern_keys)

    selectors: "List[int]" = []
    for binary_digit in f"{number:0{len(pattern_keys)}b}":
        if binary_digit == "1":
            selectors.append(1)
        else:
            selectors.append(0)

    patterns.append("".join(compress(pattern_keys, selectors)))

# same as
# patterns: "List[str]" = [
#     "".join(compress(pattern_keys, map(int, f"{x:0{len(pattern_keys)}b}")))
#     for x in range(2 ** len(pattern_keys))
# ]


def generate_outlines() -> "Iterator[Outline]":
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
                            yield Outline(
                                starter=starter,
                                attachment=attachment,
                                capitalization=(
                                    ""
                                    if not (pattern or repititions)
                                    else capitalization
                                ),
                                variant=variant,
                                pattern=pattern,
                                repititions=repititions,
                            )


key_to_number = str.maketrans(
    {
        "#": None,
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


def generate_dictionaries(
    attachment_method: "str" = emily_symbols.attachmentMethod,
    include_embedded_numbers: "bool" = False,
    json_all: "bool" = False,
) -> "Dict[str, Dict[str, str]]":
    "generates space and attachment dictionaries, with or without number embedding"
    space_dictionary = {}
    attachment_dictionary = {}
    for outline in map("".join, generate_outlines()):
        if json_all or attachment_method == "space":
            emily_symbols.attachmentMethod = "space"
            try:
                space_dictionary[outline] = emily_symbols.lookup((outline,))
            except KeyError:
                pass

            if json_all or include_embedded_numbers:
                embedded_outline = embed_numbers(outline)
                try:
                    space_dictionary[embedded_outline] = emily_symbols.lookup(
                        (embedded_outline,)
                    )
                except KeyError:
                    pass

        if json_all or attachment_method == "attachment":
            emily_symbols.attachmentMethod = "attachment"
            try:
                attachment_dictionary[outline] = emily_symbols.lookup((outline,))
            except KeyError:
                pass

            if json_all or include_embedded_numbers:
                embedded_outline = embed_numbers(outline)
                try:
                    attachment_dictionary[embedded_outline] = emily_symbols.lookup(
                        (embedded_outline,)
                    )
                except KeyError:
                    pass

    return {"space": space_dictionary, "attachment": attachment_dictionary}


def parse_args(args: "Optional[Sequence[str]]" = None) -> "Dict[str, str]":
    "parses arguments"
    parser = argparse.ArgumentParser(
        description=(
            "generates json stenographic dictionaries of Emily's "
            "system for use with openstenoproject/plover"
        )
    )

    regular_group = parser.add_argument_group(title="Regular")
    regular_group.add_argument(
        "--attachment-method",
        dest="attachment_method",
        action="store",
        choices=["space", "attachment"],
        default=emily_symbols.attachmentMethod,
        help=(
            "whether the spacing symbols indicate which sides to put "
            "spaces on, or which sides to attach to "
            f"(default is {emily_symbols.attachmentMethod})"
        ),
    )
    regular_group.add_argument(
        "--include-embedded-numbers",
        dest="include_embedded_numbers",
        action="store_true",
        default=False,
        help=(
            "include duplicate entries for outlines with the numbers embedded "
            "(e.g. both #SKWH and 1KW4 are included)"
        ),
    )
    regular_group.add_argument(
        "--directory",
        dest="directory",
        action="store",
        default=".",
        required=False,
        help=(
            "directory to put generated dictionaries in "
            "(default is the current directory)"
        ),
    )

    ci_group = parser.add_argument_group(
        title="CI", description="these override options in the Regular group"
    )
    ci_group.add_argument(
        "--json-all",
        dest="json_all",
        action="store_true",
        default=False,
        help="generate all possible JSON dictionaries",
    )

    return vars(parser.parse_args(args))  # type: ignore


def main() -> "None":
    "parses arguments and generates dictionaries"
    args = parse_args()
    attachment_method = str(args["attachment_method"])
    include_embedded_numbers = bool(args["include_embedded_numbers"])
    directory = Path(args["directory"])
    json_all = bool(args["json_all"])

    assert directory.is_dir(), f"'{directory}' is not a directory or does not exist"

    if json_all or attachment_method == "space":
        space_dictonary_path = directory / f"emily-symbols-space.json"
        assert (
            not space_dictonary_path.exists() or space_dictonary_path.is_file()
        ), f"'{space_dictonary_path}' exists and is not a file"

    if json_all or attachment_method == "attachment":
        attachment_dictionary_path = directory / f"emily-symbols-attachment.json"
        assert (
            not attachment_dictionary_path.exists()
            or attachment_dictionary_path.is_file()
        ), f"'{attachment_dictionary_path}' exists and is not a file"

    dictionaries = generate_dictionaries(
        attachment_method=attachment_method,
        include_embedded_numbers=include_embedded_numbers,
        json_all=json_all,
    )
    space_dictionary = dictionaries["space"]
    attachment_dictionary = dictionaries["attachment"]

    if space_dictionary:
        space_dictonary_path.write_text(json.dumps(space_dictionary, indent=2))

    if attachment_dictionary:
        attachment_dictionary_path.write_text(
            json.dumps(attachment_dictionary, indent=2)
        )


if __name__ == "__main__":
    main()
