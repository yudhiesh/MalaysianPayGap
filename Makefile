setup: requirements.txt
	conda create --name paygap python=3.7
	conda activate pay
	pip install -r requirements.txt

scrape_instagram:
	instaloader --login=$(username) profile malaysianpaygap --dirname-pattern={profile} --comments --no-profile-pic --post-metadata-txt="Caption: {caption}\n{likes} likes\n{comments} comments\n" --filename-pattern={date_utc:%Y}/{shortcode}
