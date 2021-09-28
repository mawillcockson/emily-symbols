"""
Plover dictionary for typing symbols while specifying spacing and capitalization
"""

# NOTE: The version was chosen arbitrarily
# GitHub lists 46 commits so far
__version__ = "0.0.46"

# Emily's Symbol Dictionary
import re

# define your starters here
#                standard  custom
uniqueStarters = ["SKWH", "#SKWH"]

# define if attachment keys define where "space"s or "attachment"s lie
attachmentMethod = "space"

LONGEST_KEY = 1

# variant format = ['', 'E', 'U', 'EU']
# if no variants exist, then a single string can be used for the symbol and the variant specifier keys will be valid but ignored
symbols = {
    uniqueStarters[0]: { # standard
        # more computer function-y symbols
        "FG"    : ["{#Tab}", "{#Backspace}", "{#Delete}", "{#Escape}"],
        "RPBG"  : ["{#Up}", "{#Left}", "{#Right}", "{#Down}"],
        "FRPBG" : ["{#Page_Up}", "{#Home}", "{#End}", "{#Page_Down}"],
        "FRBG"  : ["{#AudioPlay}", "{#AudioPrev}", "{#AudioNext}", "{#AudioStop}"],
        "FRB"   : ["{#AudioMute}", "{#AudioLowerVolume}", "{#AudioRaiseVolume}", "{#Eject}"],
        ""      : ["", "{*!}", "{*?}", "{#Space}"],
        "FL"    : ["{*-|}", "{*<}", "{<}", "{*>}"],

        # typable symbols
        "FR"     : ["!", "¬", "↦", "¡"],
        "FP"     : ["\"", "“", "”", "„"],
        "FRLG"   : ["#", "©", "®", "™"],
        "RPBL"   : ["$", "¥", "€", "£"],
        "FRPB"   : ["%", "‰", "‱", "φ"],
        "FBG"    : ["&", "∩", "∧", "∈"],
        "F"      : ["'", "‘", "’", "‚"],
        "FPL"    : ["(", "[", "<", "\{"],
        "RBG"    : [")", "]", ">", "\}"],
        "L"      : ["*", "∏", "§", "×"],
        "G"      : ["+", "∑", "¶", "±"],
        "B"      : [",", "∪", "∨", "∉"],
        "PL"     : ["-", "−", "–", "—"],
        "R"      : [".", "•", "·", "…"],
        "RP"     : ["/", "⇒", "⇔", "÷"],
        "LG"     : [":", "∋", "∵", "∴"],
        "RB"     : [";", "∀", "∃", "∄"],
        "PBLG"   : ["=", "≡", "≈", "≠"],
        "FPB"    : ["?", "¿", "∝", "‽"],
        "FRPBLG" : ["@", "⊕", "⊗", "∅"],
        "FB"     : ["\\", "Δ", "√", "∞"],
        "RPG"    : ["^", "«", "»", "°"],
        "BG"     : ["_", "≤", "≥", "µ"],
        "P"      : ["`", "⊂", "⊃", "π"],
        "PB"     : ["|", "⊤", "⊥", "¦"],
        "FPBG"   : ["~", "⊆", "⊇", "˜"],
        "FPBL"   : ["↑", "←", "→", "↓"]
    },
    uniqueStarters[1]: { # custom
        # add your own strokes here (or above, or wherever else you like)!
        ""       : "test"
    }
}


def lookup(chord):

    # normalise stroke from embedded number, to preceding hash format
    stroke = chord[0]
    if any(k in stroke for k in "1234506789"):  # if chord contains a number
        stroke = list(stroke)
        numbers = ["O", "S", "T", "P", "H", "A", "F", "P", "L", "T"]
        for key in range(len(stroke)):
            if stroke[key].isnumeric():
                stroke[key] = numbers[int(stroke[key])]  # set number key to letter
                numberFlag = True
        stroke = ["#"] + stroke
        stroke = "".join(stroke)

    # the regex decomposes a stroke into the following groups/variables:
    # starter                #STKPWHR
    # attachments                         AO
    # capitalisation                             */-
    # variants                                          EU
    # pattern                                                  FRPBLG
    # repetitions                                                         TS
    #                                       (unused: DZ)
    match = re.fullmatch(r'([#STKPWHR]*)([AO]*)([*-]?)([EU]*)([FRPBLG]*)([TS]*)', stroke)

    if match is None:
        raise KeyError
    (starter, attachments, capitalisation, variants, pattern, repetitions) = match.groups()

    if starter not in uniqueStarters:
        raise KeyError
    if len(chord) != 1:
        raise KeyError
    assert len(chord) <= LONGEST_KEY

    # calculate the attachment method, and remove attachment specifier keys
    attach = [(attachmentMethod == "space") ^ ('A' in attachments),
              (attachmentMethod == "space") ^ ('O' in attachments)]

    # detect if capitalisation is required, and remove specifier key
    capital = capitalisation == '*'

    # calculate the variant number, and remove variant specifier keys
    variant = 0
    if 'E' in variants:
        variant = variant + 1
    if 'U' in variants:
        variant = variant + 2

    # calculate the repetition, and remove repetition specifier keys
    repeat = 1
    if 'S' in repetitions:
        repeat = repeat + 1
    if 'T' in repetitions:
        repeat = repeat + 2

    if pattern not in symbols[starter]:
        raise KeyError

    # extract symbol entry from the 'symbols' dictionary, with variant specification if available
    selection = symbols[starter][pattern]
    if type(selection) == list:
        selection = selection[variant]
    output = selection

    # repeat the symbol the specified number of times
    output = output * repeat

    # attachment space to either end of the symbol string to avoid escapement,
    # but prevent doing this for retrospective add/delete spaces, since it'll
    # mess with these macros
    if selection not in ["{*!}", "{*?}"]:
        output = " " + output + " "

    # add appropriate attachment as specified (again, prevent doing this 
    # for retrospective add/delete spaces)
    if selection not in ["{*!}", "{*?}"]:
        if attach[0]:
            output = "{^}" + output
        if attach[1]:
            output = output + "{^}"

    # cancel out some formatting when using space attachment
    if attachmentMethod == "space":
        if not attach[0]:
            output = "{}" + output
        if not attach[1]:
            output = output + "{}"

    # apply capitalisation
    if capital:
        output = output + "{-|}"

    # all done :D
    return output


variant_selectors = ["", "E", "U", "EU"]
reverse_symbols: "Dict[str, Tuple[str, str]]" = {}
for starter in symbols:
    for symbol_outline in symbols[starter]:
        variants_or_translation = symbols[starter][symbol_outline]
        if not isinstance(variants_or_translation, str):
            variants = variants_or_translation
            for index, translation in enumerate(variants):
                reverse_symbols[translation] = (starter, variant_selectors[index], symbol_outline)
        else:
            translation = variants_or_translation
            reverse_symbols[translation] = (starter, "", symbol_outline)

possible_selections = "|".join(filter(None, map(re.escape, reverse_symbols)))
selection_re = re.compile(fr"(?P<selection>{possible_selections}){{1,4}}")


def removeprefix(string: str, prefix: str) -> str:
    "removes prefix from the beginning of string"
    if string.startswith(prefix):
        return string[len(prefix):]
    return string[:]


def removesuffix(string: str, suffix: str) -> str:
    "removes suffix from the end of string"
    if string.endswith(suffix):
        return string[:-len(suffix)]
    return string[:]


def reverse_lookup(output: str) -> "List[Tuple[str]]":
    """
    find outlines that, if given to lookup(), produce the output
    """
    capitalise = False
    left_attach = False
    right_attach = False

    capitalise_next_word = "{-|}"
    reset_formatting = "{}"
    attach = "{^}"

    if output.endswith(capitalise_next_word):
        capitalise = True
        output = removesuffix(output, capitalise_next_word)

    if attachmentMethod == "space":
        left_attach = output.startswith(reset_formatting)
        output = removeprefix(output, reset_formatting)
        output = removeprefix(output, attach)
        right_attach = output.endswith(reset_formatting)
        output = removesuffix(output, reset_formatting)
        output = removesuffix(output, attach)
    else:
        left_attach = output.startswith(attach)
        output = removeprefix(output, attach)
        right_attach = output.endswith(attach)
        output = removesuffix(output, attach)

    output = output.strip()

    if output == "":
        selection = output
        selection_count = 1

    else:
        match = selection_re.fullmatch(output)
        if not match:
            return []
        selection = match["selection"]
        selection_count = output.count(selection)

    (starter, variants, pattern) = reverse_symbols[selection]
    attachments = ""
    if left_attach:
        attachments += "A"
    if right_attach:
        attachments += "O"

    if capitalise:
        capitalisation = "*"
    else:
        capitalisation = "-"

    repeat_keys = {
        1: "",
        2: "S",
        3: "T",
        4: "TS",
    }
    repetitions = repeat_keys[selection_count]

    stroke = "".join([starter, attachments, capitalisation, variants, pattern, repetitions])

    if any((character in stroke) for character in "AO*EU") or stroke == starter + attachments + "-":
        stroke = stroke.replace("-", "")

    return [(stroke,)]
