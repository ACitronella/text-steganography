from PIL import Image
import numpy as np
import numpy.typing as npt

import argparse
import os

__doc__ = '''
Text stegonography
---
Change each least significant bits of the image to each bits of text.
  
merge:: (image (3d array), text (string)) -> image with text inside (3d array)
unmerge:: (image (3d array), text (string)) -> image with text inside (3d array)
'''

def bitlist_to_int(bitlist:list[int]) -> int:
    return sum([v << idx for idx, v in enumerate(bitlist[::-1])])

def write_right_most_bits(arr:npt.NDArray, bitstring:str, write_pos_offset:int=0) -> npt.NDArray:
    bits_length = min(len(arr), len(bitstring))
    for bs_idx, arr_idx in zip(range(bits_length), range(write_pos_offset, write_pos_offset+bits_length)):
        if bitstring[bs_idx] == "1":
            arr[arr_idx] = arr[arr_idx] if (arr[arr_idx]&1 == 1) else (arr[arr_idx]^1)
        else:
            arr[arr_idx] = arr[arr_idx] & 0xFE
    return arr

def zeros_padding(bitstring:str, length:int) -> str:
    if len(bitstring) < length:
        bitstring = (length - len(bitstring)) * "0" + bitstring
    return bitstring

def merge(img_path:str, text:str, output_path:str):
    _, file_extension = os.path.splitext(output_path)
    assert file_extension.lower() == ".png", "output_path must be 'png' format, since lossy compression algorithm might destroy the text information"

    img_pil = Image.open(img_path).convert("RGB")
    img = np.array(img_pil, dtype=np.uint8)
    img_pil.close()
    img_ori_shape = img.shape
    img = img.reshape(-1) # serialized array
    
    btext = ""
    for ch in text:
        binch = bin(ord(ch)).removeprefix("0b")
        binch = zeros_padding(binch, 8)
        btext += binch
    
    bin_size = min(img.shape[0]-64, len(btext))
    if bin_size > len(btext): print("Warning: the text is longer than encodable length")
    bin_text_size = bin(bin_size).removeprefix("0b")
    bin_text_size = zeros_padding(bin_text_size, 64)

    img = write_right_most_bits(img, bin_text_size) # reserve first 64 bits for header
    img = write_right_most_bits(img, btext, write_pos_offset=64)

    new_img_pil = Image.fromarray(img.reshape(img_ori_shape))
    new_img_pil.save(output_path)
    new_img_pil.close()

def unmerge(img_path:str):
    img_pil = Image.open(img_path).convert("RGB")
    img = np.array(img_pil, dtype=np.uint8)
    img_pil.close()
    img = img.reshape(-1)
    
    bimg = img & 1 # extract the right most bit
    bin_size = bitlist_to_int(bimg[:64])
    text_size = bin_size//8
    bimg = bimg[64:bimg.shape[0] - (bimg.shape[0]%8)] # exclude first 64 bits and last remainder bits
    bimg = bimg.reshape((-1, 8))
    
    extracted_chars_list = [chr(bitlist_to_int(bchar)) for bchar in bimg[:text_size]]
    extracted_text = "".join(extracted_chars_list)
    print("Extracted text: %s" % extracted_text)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    subparser = parser.add_subparsers(dest='command')

    merge_parser = subparser.add_parser('merge')
    merge_parser.add_argument('--image', required=True, help='Image path')
    merge_parser.add_argument('--text', required=True, help='Text to be hidden inside the image')
    merge_parser.add_argument('--output', required=True, help='Output image w/ text hidden inside path')

    unmerge_parser = subparser.add_parser('unmerge')
    unmerge_parser.add_argument('--image', required=True, help='Image path')

    args = parser.parse_args()

    if args.command == 'merge':
        merge(args.image, args.text, args.output)
    elif args.command == 'unmerge':
        unmerge(args.image)
