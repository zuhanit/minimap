from chk import CHK


def get_size(chk: CHK):
    dim = {
        "width": int.from_bytes(chk.sections["DIM "][0:2], "little"),
        "height": int.from_bytes(chk.sections["DIM "][2:4], "little"),
    }

    return dim


def get_tileset(chk: CHK):
    ERA = int.from_bytes(chk.sections["ERA "], "little")

    match ERA:
        case 0:
            return "badlands"
        case 1:
            return "platform"
        case 2:
            return "install"
        case 3:
            return "ashworld"
        case 4:
            return "jungle"
        case 5:
            return "Desert"
        case 6:
            return "Ice"
        case 7:
            return "Twilight"
