import cv2
import os
import sys
from mrcnn import utils
from mrcnn import model as modellib
from mrcnn.config import Config
import mrcnn.visualize
import mrcnn.model as modellib
from mrcnn.model import MaskRCNN
import uuid
import argparse
import skimage
import colorsys
import tensorflow as tf
import numpy as np
import shutil
import random
import argparse

NUM_CATS = 46
IMAGE_SIZE = 512


class FashionConfig(Config):
    NAME = "fashion"
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    NUM_CLASSES = NUM_CATS + 1
    BACKBONE = 'resnet50'

    IMAGE_MIN_DIM = IMAGE_SIZE
    IMAGE_MAX_DIM = IMAGE_SIZE
    IMAGE_RESIZE_MODE = 'none'


config = FashionConfig()

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True)
ap.add_argument("-o", "--output", required=True)
args = vars(ap.parse_args())

input_image_dir = args["input"]
output_image_dir = args["output"]

model_dir = '/content/drive/MyDrive/FGVC6/models/final/'
model_path = '/content/drive/MyDrive/FGVC6/models/final/mask_rcnn_fashion_0025.h5'

label_names = ['shirt, blouse', 'top, t-shirt, sweatshirt', 'sweater', 'cardigan', 'jacket', 'vest', 'pants', 'shorts',
               'skirt', 'coat', 'dress', 'jumpsuit', 'cape', 'glasses', 'hat',
               'headband, head covering, hair accessory',
               'tie', 'glove', 'watch', 'belt', 'leg warmer', 'tights, stockings', 'sock', 'shoe', 'bag, wallet',
               'scarf', 'umbrella',
               'hood', 'collar', 'lapel', 'epaulette', 'sleeve', 'pocket', 'neckline', 'buckle', 'zipper', 'applique',
               'bead', 'bow', 'flower',
               'fringe', 'ribbon', 'rivet', 'ruffle', 'sequin', 'tassel']

model = modellib.MaskRCNN(mode="inference", config=config, model_dir=model_dir)
model.load_weights(model_path, by_name=True)

for filename in os.listdir(input_image_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        image_path = os.path.join(input_image_dir, filename)
        print(image_path)
        img = io.imread(image_path)
        # img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        result = model.detect([resize_image(image_path)])
        r = result[0]

        if r['masks'].size > 0:
            masks = np.zeros((img.shape[0], img.shape[1], r['masks'].shape[-1]), dtype=np.uint8)
            for m in range(r['masks'].shape[-1]):
                masks[:, :, m] = cv2.resize(r['masks'][:, :, m].astype('uint8'),
                                            (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)

            y_scale = img.shape[0] / IMAGE_SIZE
            x_scale = img.shape[1] / IMAGE_SIZE
            rois = (r['rois'] * [y_scale, x_scale, y_scale, x_scale]).astype(int)

            masks, rois = refine_masks(masks, rois)
        else:
            masks, rois = r['masks'], r['rois']

        save_masked_instances(output_image_dir, img, rois, masks, r['class_ids'], ['bg'] + label_names,  r['scores'], title='image_id',
                               figsize=(16, 16))

        #display_instances_main(img, rois, masks, r['class_ids'], ['bg'] + label_names, r['scores'], title='image_id',
                               figsize=(16, 16))