import os

RULES_DIRECTORY = "/usr/local/modsecurity-crs/rules/"

def get_rule_files():
    """Retrieve all .conf files from the rules directory."""
    return [
        file for file in os.listdir(RULES_DIRECTORY) if file.endswith(".conf")
    ]
