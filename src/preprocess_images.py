#!/usr/bin/env python

from pathlib import Path, PosixPath
import re
from typing import List, Optional
import pandas as pd
import click
from loguru import logger

HASHTAG_PATTERN = r"\B#\w*[a-zA-Z]+\w*"
CAPTION_PATTERN = r"\:(.*?)\\"
LIKES_COMMENTS_PATTERN = r"(?<=\\n).+?(?=\\n)"


def get_files(
    glob_path: str,
    directory: Path,
) -> List[str]:
    """
    Get files within a certain directory
    """
    files = [
        path.resolve().as_posix()
        for path in list(
            Path(directory).glob(
                glob_path,
            )
        )
    ]
    return files


def get_text_files(
    directory: Path,
) -> List[PosixPath]:
    """
    Get all the text files within a directory
    """
    text_files = [
        path
        for path in list(Path(directory).glob("*.txt"))
        if "old" not in path.as_posix()
    ]
    return text_files


def match_pattern(
    text: str,
    pattern: str,
) -> List[Optional[str]]:
    """
    Match all text against a regex pattern
    """
    try:
        matches = re.findall(pattern, text)
        return matches
    except re.error:
        logger.error("Error finding pattern")
        raise


def remove_words(string: str) -> str:
    """
    Remove all the words from a string(keeps all the numbers)
    """
    return " ".join(word for word in string.split() if word.isdigit())


def process_captions(
    captions: List[str],
    hashtag_pattern: str,
) -> List[str]:
    """
    Removes the hashtags from a caption
    """
    new_captions = []
    for caption in captions:
        caption_updated = re.sub(hashtag_pattern, "", caption)
        new_captions.append(" ".join(caption_updated.split()))
        assert "#" not in caption_updated
    return new_captions


def process_files(
    text_files: List[PosixPath],
    directory,
    **kwargs,
):
    """
    Process the files by extracting the
    - hashtags
    - captions
    - number of likes
    - number of comments
    - image_ids
    - path to the image(locally dependent)
    """
    hashtags = kwargs.get("hashtags")
    captions = kwargs.get("captions")
    likes = kwargs.get("likes")
    comments = kwargs.get("comments")
    image_ids = kwargs.get("image_ids")
    image_paths = kwargs.get("image_paths")
    for file in text_files:
        text = file.read_text()
        hashtag = match_pattern(text=text, pattern=HASHTAG_PATTERN)
        caption = process_captions(
            match_pattern(text=text, pattern=CAPTION_PATTERN),
            hashtag_pattern=HASHTAG_PATTERN,
        )
        # If no caption then set it as NA
        caption = "".join(caption) if caption else pd.NA
        like, comment = match_pattern(
            text=text,
            pattern=LIKES_COMMENTS_PATTERN,
        )
        like = remove_words(like)
        comment = remove_words(comment)
        image_name = file.stem
        image_ids.append(image_name)
        image_files = get_files(
            glob_path=f"{image_name}*.jpg",
            directory=directory,
        )
        image_paths.append(image_files)
        likes.append(like)
        comments.append(comment)
        hashtags.append(hashtag)
        captions.append(caption)


@click.group()
def run_preprocess_images():
    ...


@run_preprocess_images.command()
def main_preprocess_images():
    current_file = Path(__file__).stem
    logger.info(f"Running {current_file}")
    directory = Path("./malaysianpaygap/2022/").resolve()
    save_path = Path("./data/posts.csv").resolve()
    if not save_path.parent.exists():
        save_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
    text_files = get_text_files(directory=directory)
    data = {
        "hashtags": [],
        "captions": [],
        "likes": [],
        "comments": [],
        "image_ids": [],
        "image_paths": [],
    }
    process_files(
        text_files=text_files,
        directory=directory,
        **data,
    )
    df = pd.DataFrame.from_dict(data=data)
    df = df.explode("image_paths")
    df.to_csv(save_path, index=False)
    logger.info(f"DataFrame saved to {save_path}")
    logger.info(f"Completed {current_file}")


if __name__ == "__main__":
    main_preprocess_images()
