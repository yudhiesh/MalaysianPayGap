# Scrapping malaysianpaygap & Extracting data from the posts

Recently [@malaysianpaygap](https://www.instagram.com/malaysianpaygap/) has gotten quite famous as a platform that enables workers throughout Malaysia to anonymously share their salaries amongst other Malaysians. Its a great initiative and I am fully supportive behind ensuring that Malaysians are not taken advantage of by companies and get a liveable wage(especially when inflation is sky high).

**UPDATE**: I am removing access to any of the data after consulting the MalaysianPayGap team as they are worried of people using the data to impart their own biases into their analysis. 

## How to run

1. Run the following to get conda environment setup

```bash
  conda create --name pay python=3.7
  conda activate pay
  pip install -r requirements.txt
```

2. Next we will need to scrape all the data from Instagram manually using BeautifulSoup!
   Just kidding I am too lazy so I will be using [InstaLoader](https://github.com/instaloader/instaloader) to do all the heavy lifting for me.
   The conda environment will have it installed for you already.

```bash
# you might need to pass in your username to login
instaloader --login=USERNAME profile malaysianpaygap --dirname-pattern={profile} --comments --no-profile-pic --post-metadata-txt="Caption: {caption}\n{likes} likes\n{comments} comments\n" --filename-pattern={date_utc:%Y}/{shortcode}
```

This should create the following directory structure:

```
|-- malaysianpaygap
|   |-- 2022
|   |   |-- CaRp-1uPh8l.jpg                    # image
|   |   |-- CaRp-1uPh8l.json.xz
|   |   |-- CaRp-1uPh8l.txt                    # text data which was specified under --post-metadata-txt
|   |   |-- CaRp-1uPh8l_comments.json          # all the comments
|   |   |-- CaT5MguPpDI.jpg
|   |   |-- CaT5MguPpDI.json.xz
|   |-- 2022-02-27_04-58-58_UTC_profile_pic.jpg
|   |-- id
|   `-- malaysianpaygap_47523401972.json.xz
|-- requirements.txt
|-- scripts
|   `-- entrypoint.sh
`-- src
    |-- __init__.py
    |-- extract_text_images.py
    |-- main.py
    |-- preprocess_comments.py
    `-- preprocess_images.py
```

**NOTE:** Please do **NOT** change the directory structure, it will break the entire pipeline.

3. You should have everything ready to run the preprocessing scripts that I have made!
   I have a bash script that runs everything in the correct order.

```bash
# make bash script runnable
chmod +x scripts/entrypoint.sh
bash scripts/entrypoint.sh
```

You should see the following output:

```
2022-03-02 22:59:54.012 | INFO     | src.preprocess_comments:main_preprocess_comments:83 - Running preprocess_comments
2022-03-02 22:59:56.276 | INFO     | src.preprocess_comments:main_preprocess_comments:110 - DataFrame saved to /Users/yravindranath/pay/data/comments.csv
2022-03-02 22:59:56.277 | INFO     | src.preprocess_comments:main_preprocess_comments:111 - Completed preprocess_comments
2022-03-02 22:59:57.537 | INFO     | src.preprocess_images:main_preprocess_images:140 - Running preprocess_images
2022-03-02 22:59:57.840 | INFO     | src.preprocess_images:main_preprocess_images:160 - DataFrame saved to /Users/yravindranath/pay/data/posts.csv
2022-03-02 22:59:57.841 | INFO     | src.preprocess_images:main_preprocess_images:161 - Completed preprocess_images
2022-03-02 22:59:59.099 | INFO     | src.extract_text_images:main_extract_text_images:54 - Running extract_text_images
Pandas Apply: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 159/159 [02:09<00:00,  1.23it/s]
2022-03-02 23:02:25.087 | INFO     | src.extract_text_images:main_extract_text_images:70 - DataFrame saved to /Users/yravindranath/pay/data/posts_text.csv
2022-03-02 23:02:25.088 | INFO     | src.extract_text_images:main_extract_text_images:71 - Completed extract_text_images
```

A new directory `data` will be created like so:

```
|-- data
|   |-- comments.csv
|   |-- comments.json
|   |-- posts.csv
|   |-- posts_text.csv
|   `-- processed_images
|       |-- CaRp-1uPh8l.jpg
|       |-- CaT5MguPpDI.jpg
|       |-- CaT6d2Yve5X.jpg
```

In the next section I will go over the data that was created.

## Data

`comments.csv` - Contains all the comments under a post

```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 2816 entries, 0 to 2815
Data columns (total 11 columns):
 #   Column           Non-Null Count  Dtype
---  ------           --------------  -----
 0   image_ids        2816 non-null   object
 1   comment_paths    2816 non-null   object
 2   id               2814 non-null   float64
 3   created_at       2814 non-null   float64
 4   text             2814 non-null   object
 5   likes_count      2814 non-null   float64
 6   answers          2814 non-null   object
 7   id.1             2814 non-null   float64 # ID of the user who commented
 8   is_verified      2814 non-null   object
 9   profile_pic_url  2814 non-null   object
 10  username         2814 non-null   object
dtypes: float64(4), object(7)
memory usage: 242.1+ KB
```

`posts_text.csv` - Contains all the posts with their text extracted through their image using OCR(Optical Character Recognition)

```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 159 entries, 0 to 158
Data columns (total 7 columns):
 #   Column       Non-Null Count  Dtype
---  ------       --------------  -----
 0   hashtags     159 non-null    object
 1   captions     139 non-null    object
 2   likes        159 non-null    int64
 3   comments     159 non-null    int64
 4   image_ids    159 non-null    object
 5   image_paths  159 non-null    object
 6   image_text   159 non-null    object
dtypes: int64(2), object(5)
memory usage: 8.8+ KB
```

## FAQ

#### I am getting a `ModuleNotFoundError: No module named 'src'` error what can I do?

This is an issue with your `PYTHONPATH`, setting it to something like `export PYTHONPATH="${PYTHONPATH}:/Users/yravindranath/REPO"` should fix it.

## Optimizations

1. So currently the entire project isn't repoducible therefore I will dockerise it soon and allow anyone to run it locally without any issues.
2. If you notice there is a slow `apply()` used for binarizing the images and extracting the text from it using OCR. I am using `swifter` to speed it up as it is.
