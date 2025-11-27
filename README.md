# Dj Authkit (dj_authkit) :lock:

> A Django app that provides a customizable, pluggable user authentication and management system.


## Table of contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Contribution](#contribution)
- [Contributors](#contributors)
- [Licence](#licence)


## Features

- [x] Django custom user model


## Coming Soon Features
- [ ] Auth views




## Installation

**using**  `pip`
```
pip install git+https://github.com/Ngahu/dj_authkit.git#egg=dj_authkit



```

 **using** `uv`

```
uv add git+https://github.com/Ngahu/dj_authkit.git#egg=dj_authkit
```


## Requirements 

- Python 3.9+
- Django 5.0.0

## Setup



Add the following to installed apps

```python


from dj_authkit import DJ_AUTHKIT_APPS

INSTALLED_APPS = [
    ...
    *DJ_AUTHKIT_APPS,
    ...

]

or 

INSTALLED_APPS = [
    ...
    "dj_authkit.config.DjAuthkit",
    "dj_authkit.apps.accounts",
    ...

]

```

In your `settings.py` add the following;

```python
from dj_authkit import DJ_AUTHKIT_AUTH_USER_MODEL

AUTH_USER_MODEL=DJ_AUTHKIT_AUTH_USER_MODEL
```