# Text steganography

The technique of hiding a text in a image.

## Implementation

Change each least significant bits of the image to each bits of text. Since an image is just 3 dimentional array of integer (some arrangement of bits), we can serialized them into 1D array. The logic work the same for text as well (array of char (integer in disguise)).  

Given an image uses RGB format in uint8, then the length of the image($x$) is $width \cdot height \cdot 3$ bits length.  
Assume that the text is in ASCII with zero in the front, then the length of the text($y$) is $numberOfCharacters\cdot8$ bits of text, each least significant bits of each bytes of the image will be replaced by each bit of the text. 

Theoretically, we must have $\frac{x}{8}$ bits for the text. However, we implement steganography in such a way that the first 64 least significant bits are reserved to store length of the text.

All least significant bits of the image will be arrange like this  
[$64$ bits (text length) | $y$ bits (text) | $\frac{x}{8} - y - 64$ bits (unused)]  
^bit 0  

However, lossy compression might destroy hidden text information. Hence, we decided to prohibit anything else but PNG format which uses lossless compression algorithm.

This code mainly support ASCII text (0 - 127) and maximum text length is $2^{64} - 64$, given the size of image is greather than this.

## Dependencies

tested on python 3.9.5, numpy 1.21.1

```bash
pip install numpy==1.21.1 Pillow
```

## Run

### merge operation

For hiding a text in an image.

```bash
python text_steganography.py merge --image=<path to an image> --text=<text to hide in the image> --output=<path for an output image>
```

### unmerge operation

For reveal a hidden text in an image

```bash
python text_steganography.py unmerge --image=<path to an image with hidden text>
```

### Examples

To hide "Cha Shak is delicious" inside the cat image in the example folder.

```bash
python text_steganography.py merge --image=example/cat.png --text="Cha Shak is delicious" --output="example/cat_with_hidden_text.png"
```

To retrive the hidden text in the generated cat image.
```bash
python text_steganography.py unmerge --image=example/cat_with_hidden_text.png
```

## Authors

- Phuriwat Angkoondittaphong 6388003
- Napahatai Sittirit 6388102
