

from .image_format import ImageFormat
from termmy.buffers import ColorBuffer
from termmy.colors import Color
from struct import Struct
from typing import ByteString
from enum import IntEnum
from math import ceil

class DIBHeader(IntEnum):
    BITMAPCOREHEADER = 12
    OS21XBITMAPHEADER = 12
    OS22XBITMAPHEADER_64 = 64
    OS22XBITMAPHEADER_16 = 16
    BITMAPINFOHEADER = 40
    BITMAPV2INFOHEADER = 52
    BITMAPV3INFOHEADER = 56
    BITMAPV4HEADER = 108
    BITMAPV5HEADER = 124

class BmpCompressionMethod(IntEnum):
    BI_RGB = 0
    BI_RLE8 = 1
    BI_RLE4 = 2
    BI_BITFIELDS = 3
    BI_JPEG = 4
    BI_PNG = 5
    BI_ALPHABITFIELDS = 6
    BI_CMYK = 11
    BI_CMYKRLE8 = 12
    BI_CMYKRLE4 = 13

BMP_IDENTIFIERS = ("BM", "BA", "CI", "CP", "CP", "IC", "PT")


def _to_int(bytes: memoryview) -> int:
    return int.from_bytes(bytes, "little")

BMP_HEADER_STRUCT = Struct("<I2HI")
BMP_BITMAPCOREHEADER_STRUCT = Struct("<I4H")
BMP_BITMAPINFOHEADER_STRUCT = Struct("<2I2H2I2i2I")

BMP_24B = Struct("3B")
BMP_32B = Struct("4B")



def is_bmp(byte_string: ByteString) -> bool:
    return byte_string[:2] not in BMP_IDENTIFIERS

def decode_bmp(byte_string: ByteString, metadata: dict) -> ColorBuffer:
    byte_string = memoryview(byte_string)
    _decode_bmp_header(byte_string, metadata)
    _decode_dib_header(byte_string, metadata)
    width, height = metadata["ImageWidth"], metadata["ImageHeight"]
    color_depth = metadata["ImageColorDepth"]
    compression_method = metadata.get("compression_method", 
                                      BmpCompressionMethod.BI_RGB)
    if compression_method != BmpCompressionMethod.BI_RGB:
        raise NotImplementedError("Decoding BMP with compression method"
                                  f" '{compression_method}' "
                                  "is not supported yet.")
    color_buffer = ColorBuffer(width=width, height=height)
    _decode_pixel_array(byte_string=byte_string,
                        metadata=metadata,
                        width=width,
                        height=height,
                        color_depth=color_depth,
                        color_buffer=color_buffer)
    return color_buffer



def _decode_bmp_header(byte_string: memoryview, metadata: dict):
    if not is_bmp(byte_string):
        raise ValueError("`byte_string` does not follow BMP format. "
                         f"It starts with {byte_string[:2].hex()}")

    (metadata["BmpFileSize"], 
     metadata["BmpReserved1"],
     metadata["BmpReserved2"], 
     metadata["BmpStartingAddress"]) = BMP_HEADER_STRUCT.unpack_from(
                                           byte_string, 2
                                       )

def _decode_dib_header(byte_string: memoryview, metadata: dict) -> None:
    header_size = _to_int(byte_string[14:18])
    metadata["BmpDIBHeader"] = DIBHeader(header_size)
    # `header_size` has been validated at this point by DIBHeader.header_name
    if header_size == DIBHeader.BITMAPCOREHEADER:
        core_info = BMP_BITMAPCOREHEADER_STRUCT.unpack_from(byte_string, 14)
        (metadata["ImageWidth"],
         metadata["ImageHeight"],
         metadata["number_of_color_planes"],
         metadata["ImageColorDepth"]) = core_info
    else:
        if header_size != DIBHeader.BITMAPINFOHEADER:
            # NOTE Is such warning a good idea? 
            # Shall I print it in read with \033[91m ?
            print(f"Warning: DIB header {repr(metadata["BmpDIBHeader"])} "
                "is not fully supported. Some metadata may be omitted.")
        info = BMP_BITMAPINFOHEADER_STRUCT.unpack_from(byte_string, 18)
        (metadata["ImageWidth"],
         metadata["ImageHeight"],
         metadata["number_of_color_planes"],
         metadata["ImageColorDepth"],
         metadata["compression_method"],
         metadata["image_size"],
         metadata["horizontal_resolution"],
         metadata["vertical_resolution"],
         metadata["number_of_colors_in_palette"],
         metadata["number_of_important_colors"]) = info

def _decode_pixel_array(byte_string: memoryview, metadata: dict,
                        width: int, height: int, color_depth: int,
                        color_buffer: ColorBuffer) -> None:
    starting = metadata["BmpStartingAddress"]
    row_width_padded = ceil(color_depth * width / 32) * 4
    actual_row_width = color_depth * width // 8
    if color_depth == 24:
        for y in range(height):
            row = BMP_24B.iter_unpack(
                byte_string[starting+y*row_width_padded
                            :starting+actual_row_width+y*row_width_padded],
            )
            row_starting_index = (height - 1 - y) * width
            for i, (b, g, r) in enumerate(row):
                color = color_buffer.data[row_starting_index + i]
                color.r = r / 255
                color.g = g / 255
                color.b = b / 255
    elif color_depth == 32:
        for y in range(height):
            row = BMP_32B.iter_unpack(
                byte_string[starting+y*row_width_padded
                            :starting+actual_row_width+y*row_width_padded],
            )
            row_starting_index = (height - 1 - y) * width
            for i, (b, g, r, a) in enumerate(row):
                color = color_buffer.data[row_starting_index + i]
                color.a = a / 255
                color.r = r / 255
                color.g = g / 255
                color.b = b / 255
    else:
        raise NotImplementedError