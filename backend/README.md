# Yog-Sothoth Backend

A small [FastAPI](https://fastapi.tiangolo.com/) based app that allows anyone to register to a Matrix homeserver with admin approval.

It uses a Redis database to temporarily store registration requests. By default, these values will only be stored for 48hs.  
Secret values are safely stored in an encrypted way.

> Yog-Sothoth knows the gate. Yog-Sothoth is the gate. Yog-Sothoth is the key and guardian of the gate.

## Basic Flow and Idea

A user creates a new registration sending optionally an email to receive notification. It receives a registration unique identifier (*rid*) and a *token* to access its data. If the user doesn't input an email it will have to manually check how the registration request status is going using its token.

When a registration request is received, an email is sent to the managers containing the *manager token* and the registration unique identifier (*rid*). Then any manager can approve or reject the registration using this token.

A registration request can be deleted by its user or automatically after a certain amount of time (48hs by default).

Currently, registrations can only be updated once: they're either approved or rejected and that's it.

Once the registration is approved, the user is required to send its username and optionally an email (again, to receive notifications). A password is sent back as response and an account is created in the Matrix homeserver with the given username.

### Security Characteristics

The user and manager tokens are stored as an Argon2id hash.  The username and password is never stored, only the user email if any (but can not be seen by any manager, no matter what).
When a manager requests user's data, it will only receive information about the status and timestamps, but won't be able to see any other information.
Both the user and managers share information using the *rid*. This permits for a user's data to remain unknown for the managers but enables potential human interaction with each other, i.e.: asking in a group if someone sent a registration request.

Note: the user email is stored in plaintext. This means that a system administrator could access the database and see this value (this means a user with root access to the Operating System, not a *manager*).

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
    * Request: `{"matrix_status": "processing", "username": "<username>", "email": "[<email>]"}` `Authorization: Basic b64(<rid>:<manager_token>)`
    * Response: *200* `{"username": "<username>", "email": "<email>", "password": "<password>", "rid": "<registration identifier>", "created": "<created datetime>", "modified": "<modified datetime>", "status": "approved", "matrix_status": "processing"}`, *401*, *403*, *404*, *422*
  * **DELETE**: Remove registration.
    * Request: `null` `Authorization: Basic b64(<rid>:<user_token>)`
    * Response: *204* `{"username": "<username>", "email": "<email>", "password": "<password>", "rid": "<registration identifier>", "created": "<created datetime>", "modified": "<modified datetime>", "status": "deleted", "matrix_status": "<pending/processing/success/failed>"}`, *401*, *403*, *404*

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
