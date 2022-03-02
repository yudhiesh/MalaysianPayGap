#!/usr/bin/env python

from pathlib import Path

from PIL import Image
import click
import pandas as pd
import pytesseract
from loguru import logger

import swifter  # need for apply func


def binarize_image(image_path, new_directory):
    """Binarize an image"""
    img = Image.open(image_path)
    thresh = 200
    fn = lambda x: 255 if x > thresh else 0
    r = img.convert("L").point(fn, mode="1")
    save_path = new_directory / image_path.name
    r.save(save_path)
    return save_path


def get_text(image_path):
    """Gets the text out of an image"""
    text = pytesseract.image_to_string(Image.open(image_path))
    return text


def process_image(row, directory):
    """
    Processes each row of the dataframe by binarizing the image then extracting
    the text data from it
    """
    image_path = Path(row["image_paths"])
    binarized_image_path = binarize_image(
        image_path=image_path,
        new_directory=directory,
    )
    text = get_text(image_path=binarized_image_path)
    row["image_text"] = text
    return row


@click.group()
def run_extract_text_images():
    ...


@run_extract_text_images.command()
def main_extract_text_images():
    file_name = Path(__file__).stem
    logger.info(f"Running {file_name}")
    posts_path = Path("./data/posts.csv").resolve()
    processed_image_dir = Path("./data/processed_images").resolve()
    save_path = Path("./data/posts_text.csv").resolve()
    if not processed_image_dir.exists():
        processed_image_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
    df = pd.read_csv(posts_path)
    df = df.swifter.apply(
        process_image,
        directory=processed_image_dir,
        axis=1,
    )
    df.to_csv(save_path, index=False)
    logger.info(f"DataFrame saved to {save_path}")
    logger.info(f"Completed {file_name}")


if __name__ == "__main__":
    main_extract_text_images()
