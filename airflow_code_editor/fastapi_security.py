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

import typing as t

from pydantic import BaseModel

try:
    from airflow.api_fastapi.core_api.openapi.exceptions import (
        create_openapi_http_exception_doc,
    )
    from airflow.api_fastapi.core_api.security import requires_access_dag

except ImportError:  # Standalone
    from fastapi import Request

    class HTTPExceptionResponse(BaseModel):
        """
        Schema for HTTPException response used in OpenAPI documentation
        """

        detail: t.Union[str, t.Dict]

    def create_openapi_http_exception_doc(responses_status_code: t.List[int]) -> t.Dict[int, t.Dict[str, t.Any]]:
        """
        Create OpenAPI documentation for HTTP exceptions
        """
        return {status_code: {"model": HTTPExceptionResponse} for status_code in sorted(responses_status_code)}

    def requires_access_dag(**kwargs: t.Any) -> t.Callable[[Request], None]:
        def inner(request: Request) -> None:
            pass

        return inner


__all__ = [
    "create_openapi_http_exception_doc",
    "requires_access_dag",
]
