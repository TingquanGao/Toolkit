import multiprocessing as mp
import os
from tqdm import tqdm
import glob
import cv2

def compress_img(img_path):
    try:
        img = cv2.imread(img_path)
        os.remove(img_path)
    except Exception as e:
        print(e)
        return

    cv2.imwrite(img_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 60])


def main(img_dir, suffix):
    img_list = glob.glob(os.path.join(img_dir, f"*.{suffix}"))
    with mp.Pool(int(mp.cpu_count() * 0.8)) as pool:
        list(tqdm(pool.imap(compress_img, img_list),
                total=len(img_list),
                desc="Compressing imgs")) 


if __name__== "__main__":
    img_dir = "det_lmssl_coco_examples/images/*/"
    suffix = "png"
    main(img_dir, suffix)