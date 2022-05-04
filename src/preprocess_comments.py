#!/usr/bin/env python

import json
from pathlib import Path
from typing import List
import click
from loguru import logger

import pandas as pd

from src.preprocess_images import get_files


# Structure of a comment within JSON object
# @dataclass
# class Comment:
#     id: int
#     created_at: int
#     text: str
#     owner: Owner
#     likes_count: int
#     answers: Optional[List[str]]


# @dataclass
# class Owner:
#     id: str
#     is_verified: bool
#     profile_pic_url: str
#     username: str


def process_comment(image_id: str, path: str, **kwargs):
    """
    Load the json of comments and extract
    - comment(check dataclass above for exact details)
    - image_id
    - comment_path
    """
    comments = kwargs.get("comments")
    image_ids = kwargs.get("image_ids")
    comment_paths = kwargs.get("comment_paths")
    with open(path) as json_file:
        comments_data = json.load(json_file)
        for comment in comments_data:
            comments.append(comment)
            image_ids.append(image_id)
            comment_paths.append(path)


def process_comments(
    image_ids_list: List[int],
    directory: Path,
    **kwargs,
):
    comment_paths = kwargs.get("comment_paths")
    for image_id in image_ids_list:
        comment_path = get_files(
            glob_path=f"{image_id}_comments.json",
            directory=directory,
        )
        # Possible for some posts not to have any comments
        if comment_path:
            path = comment_path[0]
            process_comment(image_id=image_id, path=path, **kwargs)

        else:
            comments = kwargs.get("comments")
            image_ids = kwargs.get("image_ids")
            comments.append([])
            comment_paths.append([])
            image_ids.append(image_id)


@click.group()
def run_preprocess_comments():
    ...


@run_preprocess_comments.command()
def main_preprocess_comments():
    file_name = Path(__file__).stem
    logger.info(f"Running {file_name}")
    directory = Path("./malaysianpaygap/2022/").resolve()
    data_path = Path("./data/posts.csv").resolve()
    json_path = Path("./data/comments.json").resolve()
    save_path = Path("./data/comments.csv").resolve()
    df = pd.read_csv(data_path.as_posix())
    image_ids = df["image_ids"].tolist()
    data = {
        "image_ids": [],
        "comment_paths": [],
        "comments": [],
    }
    process_comments(
        image_ids_list=image_ids,
        directory=directory,
        **data,
    )
    with open(json_path, "w") as fp:
        json.dump(data, fp)
    df = pd.DataFrame.from_dict(data)
    df_comments = df["comments"].apply(pd.Series)
    df_owner = df_comments["owner"].apply(pd.Series)
    df_final = pd.concat(
        [df, df_comments, df_owner],
        axis=1,
    ).drop(["comments", "owner"], axis=1)
    df_final.to_csv(save_path, index=False)
    logger.info(f"DataFrame saved to {save_path}")
    logger.info(f"Completed {file_name}")


if __name__ == "__main__":
    main_preprocess_comments()
