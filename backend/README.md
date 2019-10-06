# Yog-Sothoth Backend

A small [FastAPI](https://fastapi.tiangolo.com/) based app that allows anyone to register to a Matrix home server with admin approval.

It uses a Redis database to temporarily store registration requests. By default, these values will only be stored for 48hs.  
Secret values are safely stored in an encrypted way.

> Yog-Sothoth knows the gate. Yog-Sothoth is the gate. Yog-Sothoth is the key and guardian of the gate.

## API Endpoints

Since we use FastAPI, we follow OpenAPI. Check `/openapi.json` for full API specs.

* `/registrations/`: User registrations
  * **POST**: New user registration.
    * Request: `{"email": "[<email>]"}`
    * Response: *201* `{"username": "", "email": "<email>", "password": "", "rid": "<registration identifier>", "token": "<token>", "created": "<created datetime>", "modified": "<modified datetime>", "status": "pending", "matrix_status": "pending"}`, *422*
* `/registrations/:rid/`: Manage a user registration
  * **GET**: Show user information according to access token: minimal or full.
    * Request: `null` `Authorization: Basic b64(<rid>:<manager_token>)`
    * Response: *200* `{"username": null, "email": null, "password": null, "rid": "<registration identifier>", "created": "<created datetime>", "modified": "<modified datetime>", "status": "<pending/approved/rejected>", "matrix_status": "<pending/processing/success/failed>"}`, *401*, *403*, *404*
    * Request: `null` `Authorization: Basic b64(<rid>:<user_token>)`
    * Response: *200* `{"username": "<username>", "email": "<email>", "password": "<password>", "rid": "<registration identifier>", "created": "<created datetime>", "modified": "<modified datetime>", "status": "<pending/approved/rejected>", "matrix_status": "<pending/processing/success/failed>"}`, *401*, *403*, *404*
  * **PUT**: Change registration status
    * Request: `{"status": "approved"}` `Authorization: Basic b64(<rid>:<manager_token>)`
    * Response: *200* `{"username": null, "email": null, "password": null, "rid": "<registration identifier>", "created": "<created datetime>", "modified": "<modified datetime>", "status": "approved", "matrix_status": "pending"}`, *401*, *403*, *404*, *422*
    * Request: `{"status": "rejected"}` `Authorization: Basic b64(<rid>:<manager_token>)`
    * Response: *200* `{"username": null, "email": null, "password": null, "rid": "<registration identifier>", "created": "<created datetime>", "modified": "<modified datetime>", "status": "rejected", "matrix_status": "pending"}`, *401*, *403*, *404*, *422*
  * **PATCH**: Create Matrix account once approved.
    * Request: `{"matrix_status": "processing", "username": "<username>", "email": "[<email>]"}` `Authorization: Basic b64(<rid>:<user_token>)`
    * Response: *200* `{"username": "<username>", "email": "<email>", "password": "<password>", "rid": "<registration identifier>", "created": "<created datetime>", "modified": "<modified datetime>", "status": "approved", "matrix_status": "processing"}`, *401*, *403*, *404*, *422*
  * **DELETE**: Remove registration.
    * Request: `null` `Authorization: Basic b64(<rid>:<user_token>)`
    * Response: *204* `{"username": "<username>", "email": "<email>", "password": "<password>", "rid": "<registration identifier>", "created": "<created datetime>", "modified": "<modified datetime>", "status": "deleted", "matrix_status": "<pending/processing/success/failed>"}`, *401*, *403*, *404*

## Development

Clone this repo and install dependencies with `poetry install`.  
To run the application you need a Redis server and an SMTP server. These are available to you as the following [Invoke](https://www.pyinvoke.org/) tasks:

* `inv redis`
* `inv aiosmtpd`

You can then run `inv runserver -d` to launch the application in development mode.  
Check the `yog_sothoth/conf/global_settings.py` for information about all the settings which can be bypassed by creating a `yog_sothoth/conf/local_settings.py` file.

You can also lint your code with `inv lint` and `inv lint-docker`.

## License

**Yog-Sothoth** is made by [Erus](https://erudin.github.io/), [Fedr](https://fedr.cc/) and [HacKan](https://hackan.net) under GNU GPL v3.0+. You are free to use, share, modify and share modifications under the terms of that license.

    Copyright (C) 2019
     Erus (https://erudin.github.io/)
     Fedr (https://fedr.cc/)
     HacKan (https://hackan.net)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
