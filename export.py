#!/root/code/outline-api/env/bin/python

import csv
from pathlib import Path

from core.outline import OutlineBackend

export_path = Path.home()
outline = OutlineBackend()

green_line, end_line = "\033[92m", "\033[0m"

users = outline.get_all_keys().get("accessKeys")
header = [
    "id",
    "name",
    "password",
    "port",
    "method",
    "dataLimit",
    "accessUrl"
]

export_file_name = export_path.joinpath("users.csv")
with open(export_file_name, "w") as f:
    w = csv.DictWriter(f, header, delimiter=";")
    w.writeheader()

    for user in users:
        user_data = {h: user.get(h, "NULL") for h in header}
        if user_data["name"].strip() == "":
            user_data["name"] = "NULL"
        w.writerow(user_data)

print(f"{green_line}Total users in server: {len(users)}{end_line}")
print(f"{green_line}Export users success, file name is {export_file_name}{end_line}")
