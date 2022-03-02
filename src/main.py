from click import CommandCollection

from src.extract_text_images import run_extract_text_images
from src.preprocess_comments import run_preprocess_comments
from src.preprocess_images import run_preprocess_images

if __name__ == "__main__":
    cmds = [
        run_preprocess_images,
        run_preprocess_comments,
        run_extract_text_images,
    ]

    cli = CommandCollection(sources=cmds)
    cli()
