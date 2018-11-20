# PV254-recommender-system

## Cloud Vision API dependencies
- env variable `GOOGLE_APPLICATION_CREDENTIALS` needs to be set to the path where service account key is stored
- it is sufficient to place `pv254-recommender-systems-1329fedf3c97.json` inside `.secrets` folder

## Setup
1. Install virtualenv via `pip install virtualenv`.
2. Create new virtual environment `virtualenv venv`.
3. Activate virtual environment `source venv/bin/activate`.
4. Install all requirements via `pip install -r requirements.txt`

## Example usage
1. Download random images `python download_random_photos.py`.
2. Download Instagram profile `python download_ig_profile.py --profile jpancik`.
3. Annotate random images `python annotate_images.py --input resources/random-images/`.
4. Annotate IG profile images `python annotate_images.py --input profiles/jpancik/`.
5. Rank images `python rank_images.py --library profiles/jpancik/ --input resources/random-images/`.
6. Open HTML with results in `resources/random-images/recommendations.html`.
7. $$$ Profit $$$.