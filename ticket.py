import os
import re
from pathlib import Path
from datetime import datetime

import requests
import argparse
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont, ImageOps


class GIFMaker:
    def __init__(self, filename="output.gif", save_location=None, loop=True, duration=10):
        self.filename = filename
        self.loop = 0 if loop else 1
        self.save_location = save_location if save_location else os.path.abspath(
            '.')
        self.duration = duration

    def create(self, directory):
        files = sorted(os.listdir(directory))
        paths = [os.path.join(directory, f) for f in files if 'png' in f]
        image_array = [self.load(f) for f in sorted(paths)]
        image_array[0].save(os.path.join(self.save_location, self.filename),
                            save_all=True,
                            append_images=image_array[1:],
                            optimize=False,
                            duration=self.duration,
                            loop=self.loop)

    def load(self, path, text=True):
        img = Image.open(path)
        if text:
            w, h = img.size
            img = ImageOps.pad(img, (w, h + 20), method=3, color=0, centering=(0, 0))
            font = ImageFont.load_default()
            draw = ImageDraw.Draw(img)
            filename = Path(path).stem
            draw.text((0, h + 2), filename, font=font)
        return img


def parse(event, url):
    root = 'https://www.artsticket.com.tw'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    image = soup.select('.mapDiv')[0].select('img')[0].attrs['src']
    image_url = root + image
    img_data = requests.get(image_url).content

    areas = set([i.attrs['title'] for i in soup.select('area')]) 
    left = [int(re.findall(r'尚餘：(\d+)', i)[0]) for i in list(areas)] 
    left = sum(left)                                                    

    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')

    os.makedirs(event, exist_ok=True)
    with open(f"{event}/{current_time}_{left}.png", 'wb') as f:
        f.write(img_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--event",
                        default="未命名活動",
                        type=str,
                        help="設定活動名稱")
    parser.add_argument("--url",
                        type=str,
                        help="設定兩廳院售票網活動網址")
    parser.add_argument("--gif",
                        action="store_true",
                        help="儲存成gif檔")
    args = parser.parse_args()

    event = args.event
    url = args.url

    parse(event, url)

    if args.gif:
        maker = GIFMaker(save_location=event)
        maker.create(event)
