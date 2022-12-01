from argparse import ArgumentParser
from PIL import Image

parser = ArgumentParser()
parser.add_argument('filename', type=str)
args = parser.parse_args()

im = Image.open(args.filename)

for name, height in { 'sm': 120,
    'lg': 880, '192': 192, '512': 512}.items():
    print(name, height)
    width = im.width * height // im.height
    im_1 = im.resize((width, height), Image.BILINEAR)
    im_1.save('gitea-' + name + '.png')
