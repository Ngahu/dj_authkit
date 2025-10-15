<p align="left"><a href="https://www.shopyangu.com/" target="_blank"><img src="assets/logo.png" width="140"></a></p>


# Shopyangu Payments :dollar: :pound: :yen: :euro:

> Payment Library For Most Public Payment API's in Kenya and hopefully Africa.


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
pip install git+https://github.com/Shopyangu-engineering/shopyangu_payments.git#egg=shopyangu_payments

```

 **using** `uv`

```
uv add git+https://github.com/Shopyangu-engineering/shopyangu_payments.git#egg=shopyangu_payments
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