
import pandas as pd
import re
from pathlib import Path

# ==========================================
# STUDENT DATA ETL AUTOMATION
# Week-03 / Day-12
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = INPUT_DIR / "students_raw.csv"

# ==========================================
# STEP 1: EXTRACT - LOCATE SOURCE CSV
# ==========================================

if not INPUT_FILE.exists():
    alternative = BASE_DIR / "students_raw.csv"

    if alternative.exists():
        INPUT_FILE = alternative
    else:
        candidates = [
            p for p in INPUT_DIR.glob("*.csv")
            if p.is_file()
        ]

        if len(candidates) == 1:
            INPUT_FILE = candidates[0]
        else:
            raise FileNotFoundError(
                "Source CSV not found.\n"
                "Place students_raw.csv inside "
                "the Day-12/input folder.\n"
                f"Expected location: {INPUT_FILE}"
            )

print("=" * 55)
print("STUDENT ETL AUTOMATION STARTED")
print("=" * 55)
print("Reading:", INPUT_FILE)

# ==========================================
# STEP 2: READ SOURCE FILE
# ==========================================

df = pd.read_csv(
    INPUT_FILE,
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig"
)

df.columns = df.columns.str.strip()

required_columns = [
    "Student_ID",
    "Name",
    "Email",
    "Phone",
    "Course",
    "Fee_Paid",
    "City",
    "Enrolled_Date"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print("\nSTEP 2: DATA EXTRACTED")
print("Total records:", len(df))
print("Available columns:", df.columns.tolist())

# Save original values for audit
original_df = df.copy()

# ==========================================
# STEP 3: TRANSFORM - DATA CLEANING
# ==========================================

print("\nSTEP 3: CLEANING DATA")

# 3.1 Remove leading/trailing and extra spaces
for col in required_columns:
    df[col] = (
        df[col]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

# 3.2 Standardize student attributes
df["Email"] = df["Email"].str.lower()
df["Name"] = df["Name"].str.title()
df["City"] = df["City"].str.title()
df["Course"] = df["Course"].str.title()
df["Student_ID"] = df["Student_ID"].str.upper()

# 3.3 Clean phone number formatting
df["Phone"] = df["Phone"].str.replace(
    r"[\s().-]", "", regex=True
)

# Convert country code +91 / 91 where applicable
df["Phone"] = df["Phone"].apply(
    lambda x: x[3:] if x.startswith("+91")
    and len(x) == 13
    else x[2:] if x.startswith("91")
    and len(x) == 12
    else x
)

# 3.4 Standardize Fee_Paid
fee_mapping = {
    "true": "True",
    "yes": "True",
    "1": "True",
    "paid": "True",
    "false": "False",
    "no": "False",
    "0": "False",
    "unpaid": "False"
}

df["Fee_Paid"] = df["Fee_Paid"].apply(
    lambda x: fee_mapping.get(x.lower(), "")
)

# 3.5 Validate email format
email_pattern = (
    r"^[A-Za-z0-9._%+-]+@"
    r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

email_valid = df["Email"].str.fullmatch(
    email_pattern, na=False
)

# 3.6 Validate Indian mobile number
phone_valid = df["Phone"].str.fullmatch(
    r"[6-9][0-9]{9}", na=False
)

# 3.7 Validate enrollment date
parsed_dates = pd.to_datetime(
    df["Enrolled_Date"],
    format="%Y-%m-%d",
    errors="coerce"
)

date_valid = parsed_dates.notna()

# 3.8 Identify duplicate student IDs
duplicate_ids = (
    df["Student_ID"].ne("") &
    df["Student_ID"].duplicated(keep=False)
)

# 3.9 Check mandatory values
mandatory_columns = required_columns

missing_values = df[mandatory_columns].eq("").any(axis=1)

# 3.10 Build data quality validation results
df["Email_Valid"] = email_valid
df["Phone_Valid"] = phone_valid
df["Date_Valid"] = date_valid
df["Duplicate_ID"] = duplicate_ids

def validate_record(row):
    issues = []

    if missing_values.loc[row.name]:
        issues.append("Missing required field")

    if not row["Email_Valid"]:
        issues.append("Invalid email")

    if not row["Phone_Valid"]:
        issues.append("Invalid phone")

    if not row["Date_Valid"]:
        issues.append("Invalid enrollment date")

    if row["Duplicate_ID"]:
        issues.append("Duplicate student ID")

    if row["Fee_Paid"] == "":
        issues.append("Invalid fee status")

    if issues:
        return pd.Series([
            "Needs Review",
            "; ".join(issues)
        ])

    return pd.Series(["Valid", ""])

df[["Data_Status", "Validation_Issues"]] = df.apply(
    validate_record,
    axis=1
)

# ==========================================
# STEP 4: LOAD - EXPORT OUTPUT CSV FILES
# ==========================================

cleaned_file = OUTPUT_DIR / "students_cleaned.csv"
review_file = OUTPUT_DIR / "students_review.csv"
summary_file = OUTPUT_DIR / "etl_summary.csv"

# All cleaned and validated records
df.to_csv(
    cleaned_file,
    index=False,
    encoding="utf-8-sig"
)

# Records requiring correction
review_df = df[
    df["Data_Status"] == "Needs Review"
].copy()

review_df.to_csv(
    review_file,
    index=False,
    encoding="utf-8-sig"
)

# ==========================================
# STEP 5: GENERATE ETL SUMMARY
# ==========================================

total_records = len(df)
valid_records = int(
    (df["Data_Status"] == "Valid").sum()
)
review_records = int(
    (df["Data_Status"] == "Needs Review").sum()
)

summary = pd.DataFrame({
    "Metric": [
        "Input Records",
        "Output Records",
        "Valid Records",
        "Needs Review",
        "Invalid Emails",
        "Invalid Phones",
        "Invalid Dates",
        "Duplicate Student IDs"
    ],
    "Count": [
        total_records,
        len(df),
        valid_records,
        review_records,
        int((~email_valid).sum()),
        int((~phone_valid).sum()),
        int((~date_valid).sum()),
        int(duplicate_ids.sum())
    ]
})

summary.to_csv(
    summary_file,
    index=False,
    encoding="utf-8-sig"
)

# ==========================================
# STEP 6: DISPLAY EXECUTION SUMMARY
# ==========================================

print("\n" + "=" * 55)
print("ETL EXECUTION SUMMARY")
print("=" * 55)

print(summary.to_string(index=False))

print("\nGenerated files:")
print("1.", cleaned_file)
print("2.", review_file)
print("3.", summary_file)

print("\nETL PROCESS COMPLETED SUCCESSFULLY")
