#!/usr/bin/env python
import os
import json

THEME_PATH = "airflow_code_editor/static/css/theme"
THEME_JS_PATH = "src/themes.js"

with open(THEME_JS_PATH, "w") as f:
    f.write("export default ")
    f.write(
        json.dumps(
            sorted(
                ["default"]
                + [x[:-4] for x in os.listdir(THEME_PATH) if x.endswith(".css")]
            )
        )
    )
    f.write(";\n")
