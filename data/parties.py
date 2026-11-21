"""Voteview party codes and member names, shared by build_hill_map.py and build_districts.py."""
# Voteview party codes -> (name, family). Families match The Hill's colors (D, R, F, DR, NR, W; anything else O).
PARTY = {
    1: ("Federalist", "F"), 5000: ("Pro-Administration", "F"), 13: ("Democratic-Republican", "DR"), 4000: ("Anti-Administration", "DR"),
    22: ("Adams", "NR"), 1275: ("Anti-Jacksonian", "NR"), 8000: ("Adams-Clay Federalist", "NR"), 8888: ("Adams-Clay Republican", "NR"),
    26: ("Anti-Masonic", "O"), 29: ("Whig", "W"), 48: ("States' Rights Whig", "W"),
    100: ("Democratic", "D"), 101: ("Jackson Democrat", "D"), 555: ("Jacksonian", "D"), 1346: ("Jackson Republican", "D"), 7000: ("Jackson Federalist", "D"),
    6000: ("Crawford Federalist", "DR"), 6666: ("Crawford Republican", "DR"), 7777: ("Crawford Republican", "DR"),
    200: ("Republican", "R"), 3333: ("Opposition", "R"), 3334: ("Opposition", "R"), 4444: ("Unionist", "R"), 203: ("Unconditional Unionist", "R"),
    206: ("Unionist", "O"), 208: ("Liberal Republican", "O"), 300: ("Free Soil", "O"), 310: ("American (Know-Nothing)", "O"),
    326: ("Greenback", "O"), 328: ("Independent", "O"), 329: ("Independent Democrat", "O"), 331: ("Independent Republican", "O"),
    340: ("Populist", "O"), 347: ("Prohibition", "O"), 354: ("Silver Republican", "O"), 355: ("Union Labor", "O"), 370: ("Progressive", "O"),
    380: ("Socialist", "O"), 402: ("Liberal", "O"), 522: ("American Labor", "O"), 537: ("Farmer-Labor", "O"), 1060: ("Silver", "O"),
    44: ("Nullifier", "O"), 46: ("States' Rights", "O"), 37: ("Constitutional Unionist", "O"), 112: ("Conservative", "O"), 114: ("Readjuster", "O"),
    117: ("Readjuster Democrat", "O"), 1111: ("Liberty", "O"), 1116: ("Conservative Republican", "O"), 403: ("Law and Order", "O"),
    108: ("Anti-Lecompton Democrat", "O"), 40: ("Anti-Lecompton Democrat", "O"), 41: ("Independent Democrat", "O"), 103: ("Democrat and Unionist", "O"),
}
party = lambda code: PARTY.get(code, ("Other", "O"))

def nice(n):
    """Voteview 'LAST, First Middle, Jr.' -> 'First Middle Last Jr.'"""
    parts = [p.strip() for p in n.split(",")]
    last = " ".join(w.capitalize() if not w[:2].lower() == "mc" else "Mc" + w[2:].capitalize() for w in parts[0].split())
    last = "-".join(x[:1].upper() + x[1:] for x in last.split("-"))
    first = parts[1] if len(parts) > 1 else ""
    first = first.split("(")[0].strip() if "(" in first and first.split("(")[0].strip() else first.replace("(", "").replace(")", "")
    return " ".join(x for x in [first, last] + parts[2:] if x)

