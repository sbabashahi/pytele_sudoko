import cv2
import redis
import os
import io
import numpy as np
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import ContextTypes


pytesseract.pytesseract.tesseract_cmd = r"/usr/local/bin/tesseract"

frames = []


async def get_binary_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> cv2.typing.MatLike:
    if update.message.document:
        file_id = update.message.document.file_id
    else:
        file_id = update.message.photo[-1].file_id
    file = await context.bot.get_file(file_id)
    dl_file = io.BytesIO()
    await file.download_to_memory(dl_file)
    dl_file.seek(0)
    image = np.asarray(bytearray(dl_file.read()), dtype="uint8")
    return cv2.imdecode(image, cv2.IMREAD_COLOR)


def show_image(gray_scale: cv2.typing.MatLike, timeout: int = 200):
    return
    if not os.getenv('DEBUG', False):
        return
    cv2.imshow("image", gray_scale)
    cv2.waitKey(timeout)
    rgb_frame = cv2.cvtColor(gray_scale, cv2.COLOR_BGR2RGB)
    frames.append(Image.fromarray(rgb_frame))


def read_image_from_local(path: str) -> np.ndarray:
    return cv2.imread(path, 0)


def extract_sudoku(gray_scale: cv2.typing.MatLike) -> list[int]:
    img_bin = cv2.Canny(gray_scale, 50, 110)
    show_image(img_bin)
    dil_kernel = np.ones((3, 3), np.uint8)
    img_bin = cv2.dilate(img_bin, dil_kernel, iterations=1)
    show_image(img_bin)

    line_min_width = 20

    kernel_h = np.ones((1, line_min_width), np.uint8)
    img_bin_h = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_h)
    show_image(img_bin_h)
    kernel_v = np.ones((line_min_width, 1), np.uint8)
    img_bin_v = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel_v)
    show_image(img_bin_v)
    img_bin_final = img_bin_h | img_bin_v
    final_kernel = np.ones((3, 3), np.uint8)
    img_bin_final = cv2.dilate(img_bin_final, final_kernel, iterations=1)
    show_image(img_bin_final)
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(~img_bin_final, connectivity=8, ltype=cv2.CV_32S)
    data = []
    for x, y, w, h, area in stats[1:]:
        image = gray_scale[y:y + h, x:x + w]
        found_text = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
        found_text = found_text.replace('\n', '')
        if found_text:
            try:
                found_text = int(found_text)
            except ValueError:
                found_text = ''
        else:
            found_text = 0  # replacing '' with 0
        show_image(
            cv2.rectangle(gray_scale, (x, y), (x + w, y + h), (0, 255, 0), 2))  # place of image in gray_scale
        data.append(found_text)

    if len(data) != 81:
        raise Exception("Couldn't extract sudoku")
    return data


def get_cache_client() -> redis.Redis:
    return redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=os.getenv('REDIS_PORT', 6379),
        db=os.getenv('REDIS_DB', 0),
    )
