# PV254-recommender-system
[![Heroku](http://heroku-badge.herokuapp.com/?app=pv254-recommender-system&svg=1)](https://pv254-recommender-system.herokuapp.com/)


## Cloud Vision API dependencies
- env variable `GOOGLE_APPLICATION_CREDENTIALS` needs to be set to the path where service account key is stored
- it is sufficient to place `access.json` inside `.secrets` folder

## Setup
1. Install virtualenv via `pip install virtualenv` (alternatively `pip3 install virtualenv`).
2. Create new virtual environment `virtualenv venv` (alternatively `virtualenv -p python3 venv`).
3. Activate virtual environment `source venv/bin/activate` (Windows: `venv\Scripts\activate`).
4. Install all requirements via `pip install -r requirements.txt`
5. Leaving virtual environment: `deactivate`.

## Example usage
1. Export PYTHONPATH to root dir ``export PYTHONPATH=`pwd` ``.
2. Download random images `python scripts/download_random_photos.py`.
3. Download Instagram profile `python scripts/download_ig_profile.py --profile jpancik`.
4. Annotate random images `python scripts/annotate_images.py --input resources/random-images/`.
5. Annotate IG profile images `python scripts/annotate_images.py --input profiles/jpancik/`.
6. Rank images `python scripts/rank_images.py --library profiles/jpancik/ --input random-images/`.
7. Open HTML with results in `resources/random-images/recommendations.html`.
8. \$$$ Profit $$$.


## Django frontend
1. Perform all steps in Setup
2. Run server:
    * dev `python manage.py runserver` is listening on `127.0.0.1:8000`
    * prod `gunicorn frontend.wsgi`

## Export profiles to CSV
1. python scripts/export_label_count_from_profiles_to_csv.py --dbfile <PATH_TO_DB_FILE> --output <PATH_TO_EXPORT_CSV> --min_score <OPTIONAL_MIN_SCORE>

## How to use "Galajdator"
1. Download model from  `https://www.dropbox.com/s/buix0deqlks4312/lexvec.commoncrawl.ngramsubwords.300d.W.pos.bin.gz?dl=1`
2. Unzip it  to `/lib/lexvec_model/lexvec_model.bin`