## Dependencies

You first need to install `postgresql`, `pip`, `virtualenv` and `pipenv`.
Now go to the project folder and run `pipenv install`. This will create a
virtual environment and install all the necessary packages.

Create the database by running `./create_db.sh` from the `/bin` folder.

When pulling, run `pipenv install` to install missing packages.

## Installing new packages

When installing a new package run `pipenv install <package_name>`.
When uninstalling a package run `pipenv uninstall <package_name>`.
For example, `pipenv install Flask`, `pipenv uninstall Flask`.

## Running the project

Run `pipenv run python3 app.py` from within the project folder.

## Upgrade and Migrate DB

After making changes to the DB run `pipenv run python3 manage.py db migrate`.
To upgrade the DB run `pipenv run python3 manage.py db upgrade`.

## ENV variables

```
    - DATABASE_URL="postgresql:///app_db"
    - APP_SETTINGS="config.DevelopmentConfig"
    - SECRET_KEY="this is a very long secret key"
    - UPLOAD_PROPOSALS_FOLDER="folder path"
```
