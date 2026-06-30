import pandas as pd

# Explicit hand-name normalisation map.
# Only corrects capitalisation differences and unambiguous model-name aliases.
_HAND_NAME_MAP = {
    # Barrett Hand model aliases (same platform, different label)
    "Barrett Hand BH-280":          "Barrett Hand",
    "Barrett Hand BH8-282":         "Barrett Hand",
}


def load_hands(csv_path="data/Robotic_hands_Included_articles.csv",
               na_values=None,
               drop_cols=None):
    if na_values is None:
        na_values = ["unknown", "Unknown", "-", "x", "-1"]
    if drop_cols is None:
        drop_cols = ["Comments"]
    df = pd.read_csv(csv_path, na_values=na_values)
    _fill_nan_handnames(df)
    df["HandName"] = df["HandName"].map(lambda name: _HAND_NAME_MAP.get(name, name))
    _enumerate_custom_hands(df)
    for column in df.columns:
        df = df.replace({column: {"Yes": True, "No": False}})
    df = df.replace({"Reposition / Opposition": {
        "Switching": True, "Neither of the two": False,
        "Either of the two": False, "Opposition": False, "Reposition": False,
    }})
    df = df.replace({"Abduction / Adduction": {
        "Switching": True, "Neither of the two": False,
        "Adduction": False, "Abduction": False,
    }})
    df = df.replace({"Flexion/Extension": {
        "Switching": True, "Neither of the two": False, "Flexion": False,
    }})
    df = df.replace({"Num. of Fingers": {">5": "6"}})
    df.drop(drop_cols, axis=1, inplace=True, errors="ignore")
    return df


def _fill_nan_handnames(df):
    for i in range(len(df)):
        if pd.isnull(df.at[i, "HandName"]):
            df.at[i, "HandName"] = "Custom hand"


def _enumerate_custom_hands(df):
    j = 0
    for i in range(len(df)):
        if df.at[i, "HandName"].lower().startswith("custom hand"):
            j += 1
            df.at[i, "HandName"] = f"Custom hand {j:02d}"
