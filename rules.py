import os

RULES_DIRECTORY = "/usr/local/modsecurity-crs/rules/"

# Descriptive names mapping
RULE_DESCRIPTIONS = {
    "REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf": "Custom Exclusions Before CRS",
    "REQUEST-901-INITIALIZATION.conf": "Initialization Rules",
    "REQUEST-905-COMMON-EXCEPTIONS.conf": "Common Exceptions",
    "REQUEST-911-METHOD-ENFORCEMENT.conf": "Method Enforcement",
    "REQUEST-913-SCANNER-DETECTION.conf": "Scanner Detection",
    "REQUEST-920-PROTOCOL-ENFORCEMENT.conf": "Protocol Enforcement",
    "REQUEST-921-PROTOCOL-ATTACK.conf": "Protocol Attack Protection",
    "REQUEST-922-MULTIPART-ATTACK.conf": "Multipart Attack Protection",
    "REQUEST-930-APPLICATION-ATTACK-LFI.conf": "LFI (Local File Inclusion) Protection",
    "REQUEST-931-APPLICATION-ATTACK-RFI.conf": "RFI (Remote File Inclusion) Protection",
    "REQUEST-932-APPLICATION-ATTACK-RCE.conf": "RCE (Remote Code Execution) Protection",
    "REQUEST-933-APPLICATION-ATTACK-PHP.conf": "PHP Attack Protection",
    "REQUEST-934-APPLICATION-ATTACK-GENERIC.conf": "Generic Attack Protection",
    "REQUEST-941-APPLICATION-ATTACK-XSS.conf": "XSS (Cross-Site Scripting) Protection",
    "REQUEST-942-APPLICATION-ATTACK-SQLI.conf": "SQL Injection Protection",
    "REQUEST-943-APPLICATION-ATTACK-SESSION-FIXATION.conf": "Session Fixation Protection",
    "REQUEST-944-APPLICATION-ATTACK-JAVA.conf": "Java Attack Protection",
    "REQUEST-949-BLOCKING-EVALUATION.conf": "Blocking Evaluation",
    "RESPONSE-950-DATA-LEAKAGES.conf": "Data Leakages",
    "RESPONSE-951-DATA-LEAKAGES-SQL.conf": "SQL Data Leakages",
    "RESPONSE-952-DATA-LEAKAGES-JAVA.conf": "Java Data Leakages",
    "RESPONSE-953-DATA-LEAKAGES-PHP.conf": "PHP Data Leakages",
    "RESPONSE-954-DATA-LEAKAGES-IIS.conf": "IIS Data Leakages",
    "RESPONSE-955-WEB-SHELLS.conf": "Web Shells Protection",
    "RESPONSE-959-BLOCKING-EVALUATION.conf": "Response Blocking Evaluation",
    "RESPONSE-980-CORRELATION.conf": "Response Correlation Rules",
}

def get_rule_files():
    """Retrieve all .conf files and add descriptive names."""
    files = [
        file for file in os.listdir(RULES_DIRECTORY) if file.endswith(".conf")
    ]
    # Map files to descriptions
    return [
        {"filename": file, "description": RULE_DESCRIPTIONS.get(file, "Unknown Rule")}
        for file in files
    ]
