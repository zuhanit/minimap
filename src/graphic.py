import numpy as np
import struct
from tqdm import tqdm
from chk import CHK
from tileset import CV5
from tileset.terrain import VF4, VR4, VX4, WPE, Tilesets
from utils import map


class Renderer:
    def __init__(self, tileset: Tilesets):
        self.cv5 = CV5(tileset)
        self.vf4 = VF4(tileset)
        self.vx4 = VX4(tileset)
        self.vr4 = VR4(tileset)
        self.wpe = WPE(tileset)

    def __set_tileset__(self, tileset: Tilesets):
        self.cv5 = CV5(tileset)
        self.vf4 = VF4(tileset)
        self.vx4 = VX4(tileset)
        self.wpe = WPE(tileset)
        self.vr4 = VR4(tileset)

    def render_map(self, chk: CHK):
        tileset = map.get_tileset(chk)
        self.__set_tileset__(tileset)

        dimension = map.get_size(chk)
        image = np.zeros(
            (32 * dimension["height"], 32 * dimension["width"], 3), np.uint8
        )
        unpacked_mtxm = struct.unpack(
            f"{dimension["height"] * dimension["width"]}H", chk.sections["MTXM"]
        )

        for y in tqdm(range(dimension["height"])):
            for x in range(dimension["width"]):
                group_id = unpacked_mtxm[y * dimension["width"] + x] >> 4
                megatile_id = unpacked_mtxm[y * dimension["width"] + x] & 0xF
                group = self.cv5.tiles[group_id]
                mt_id = group["tiles"][megatile_id]
                minitiles = self.vx4.graphics[mt_id]

                for suby in range(4):
                    for subx in range(4):
                        flipped = minitiles[suby * 4 + subx]["flipped"]
                        vr4_id = minitiles[suby * 4 + subx]["vr4_id"]
                        vr4_value = self.vr4.graphics[vr4_id]

                        draw_offsetx = x * 32 + subx * 8
                        draw_offsety = y * 32 + suby * 8

                        for j in range(8):
                            for i in range(8):
                                drawx = draw_offsetx + (7 - i if flipped else i)
                                drawy = draw_offsety + j

                                wpe_value = self.wpe.graphics[vr4_value[j * 8 + i]]
                                color = [
                                    wpe_value["blue"],
                                    wpe_value["green"],
                                    wpe_value["red"],
                                ]
                                image[drawy][drawx] = color

        return image

    def render_tile(self, tile_id: int):
        image = np.zeros((32, 32, 3), np.uint8)
        minitiles = self.vx4.graphics[tile_id]

        for x in range(4):
            for y in range(4):
                flipped = minitiles[y * 4 + x]["flipped"]
                vr4_id = minitiles[y * 4 + x]["vr4_id"]
                vr4_value = self.vr4.graphics[vr4_id]

                draw_offsetx = x * 8
                draw_offsety = y * 8

                for subx in range(8):
                    for suby in range(8):
                        drawx = draw_offsetx + (7 - subx if flipped else subx)
                        drawy = draw_offsety + suby

                        wpe_value = self.wpe.graphics[vr4_value[suby * 8 + subx]]
                        color = [
                            wpe_value["blue"],
                            wpe_value["green"],
                            wpe_value["red"],
                        ]
                        image[drawy][drawx] = color

        return image

    def render_minimap(self, chk: CHK):
        tileset = map.get_tileset(chk)
        self.__set_tileset__(tileset)

        image = np.zeros((128, 128, 3), np.uint8)

        dimension = map.get_size(chk)
        unpacked_mtxm = struct.unpack(
            f"{dimension["height"] * dimension["width"]}H", chk.sections["MTXM"]
        )

        higher = [dimension["width"], dimension["height"]].sort()[1]

        match [higher > 64, higher > 128]:
            case [False, _]:
                ...
            case [True, False]:
                ...
            case [_, True]:
                ...
