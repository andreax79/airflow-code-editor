#!/usr/bin/env python
#
#   Copyright 2019 Andrea Bonomi <andrea.bonomi@gmail.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License
#

import time

from airflow.configuration import conf
from itsdangerous import URLSafeSerializer

__all__ = ["create_presigned", "decode_presigned"]


def get_signer() -> URLSafeSerializer:
    """
    Get a signer instance
    """
    secret_key = conf.get_mandatory_value("core", "fernet_key")
    return URLSafeSerializer(secret_key)


def create_presigned(filename: str, expires_in: int = 300) -> str:
    """
    Generate a signed token with expiry
    """
    payload = {"filename": filename, "exp": int(time.time()) + expires_in}
    return get_signer().dumps(payload)


def decode_presigned(token: str) -> str:
    """
    Decode and verify a signed token
    """
    data = get_signer().loads(token)
    if data["exp"] < int(time.time()):
        raise ValueError("Token has expired")
    return data["filename"]
