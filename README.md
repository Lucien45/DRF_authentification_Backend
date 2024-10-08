# GoCardless sample application

## Setup

The first thing to do is to clone the repository:

```sh
$ git  https://github.com/Lucien45/DjangoRestFramework_authentification_Backend.git
$ cd DjangoRestFramework_authentification_Backend
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ virtualenv2 --no-site-packages env
$ source env/bin/activate
```

Then install the dependencies:

```sh
(env)$ pip install -r requirements.txt
```
Note the `(env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv2`.

Once `pip` has finished downloading the dependencies:
```sh
(env)$ cd project
(env)$ python manage.py makemigrations
(env)$ python manage.py createsuperuser
(env)$ python manage.py runserver
```
