# ==================
# library imports
# ==================

import pandas as pd
import numpy as np
import ast
import re
import json


# ============================================================
# 1. Function to clean and expand the "ratings" column
# ============================================================

def clean_ratings_column(df, ratings_col):

    def parse_rating_raw(raw):
        """Convert the string to a Python list if necessary."""

        if isinstance(raw, list):
            return raw

        if not isinstance(raw, str) or raw.strip() == "":
            return []

        # --------------------
        # Normal attempt
        # --------------------
        try:
            return ast.literal_eval(raw)
        except:
            pass

        # --------------------------
        # Regex cleanup as fallback
        # --------------------------
        fixed = re.sub(r"([a-zA-Z_]+):", r"'\1':", raw)  # keys without quotes
        fixed = fixed.replace("None", "0")

        try:
            return ast.literal_eval(fixed)
        except:
            return []

    def parse_rating_list(rating_list):

        categories = {
            "exceptional": {"percent": 0, "count": 0},
            "recommended": {"percent": 0, "count": 0},
            "meh":         {"percent": 0, "count": 0},
            "skip":        {"percent": 0, "count": 0},
        }

        if not isinstance(rating_list, list):
            return pd.Series({col: 0 for col in [
                "exceptional_percent","recommended_percent","meh_percent","skip_percent",
                "exceptional_count","recommended_count","meh_count","skip_count",
                "rating_positive_ratio","rating_negative_ratio",
                "rating_total_votes","rating_main_category"
            ]})

        # --------------------------
        # Real filling
        # --------------------------
        for entry in rating_list:
            name = entry.get("title", "").lower()
            if name in categories:
                categories[name]["percent"] = entry.get("percent", 0)
                categories[name]["count"]   = entry.get("count", 0)

        total_votes = sum(categories[c]["count"] for c in categories)

        positive = categories["exceptional"]["percent"] + categories["recommended"]["percent"]
        negative = categories["meh"]["percent"] + categories["skip"]["percent"]

        # --------------------------
        # Dominant category
        # --------------------------
        main_category = max(categories, key=lambda x: categories[x]["percent"])

        return pd.Series({
            "exceptional_percent": categories["exceptional"]["percent"],
            "recommended_percent": categories["recommended"]["percent"],
            "meh_percent":         categories["meh"]["percent"],
            "skip_percent":        categories["skip"]["percent"],

            "exceptional_count": categories["exceptional"]["count"],
            "recommended_count": categories["recommended"]["count"],
            "meh_count":         categories["meh"]["count"],
            "skip_count":        categories["skip"]["count"],

            "rating_positive_ratio": positive,
            "rating_negative_ratio": negative,
            "rating_total_votes": total_votes,
            "rating_main_category": main_category
        })

    # --------------------------
    # Conversion string → list
    # --------------------------
    df["ratings_parsed"] = df[ratings_col].apply(parse_rating_raw)

    # --------------------------
    # Column Extraction
    # --------------------------
    ratings_expanded = df["ratings_parsed"].apply(parse_rating_list)

    # --------------------------
    # Fusion
    # --------------------------
    df = pd.concat([df, ratings_expanded], axis=1)

    # --------------------------
    # Round ratio to 2 decimals
    # --------------------------
    df["rating_positive_ratio"] = df["rating_positive_ratio"].round(2)
    df["rating_negative_ratio"] = df["rating_negative_ratio"].round(2)
    df = df.drop(columns=[ratings_col, "ratings_parsed"])

    return df


# =======================================================================
# 2. Function to clean and expand the "added_by_status" column
# ======================================================================

def expand_added_by_status(df, col):
    # --------------------------------
    # Fields to extract
    # --------------------------------
    keys = ["yet", "owned", "beaten", "toplay", "dropped", "playing"]
    
    for key in keys:
        pattern = rf"'{key}':\s*(\d+)"
        df[f"status_{key}"] = (
            df[col]
            .astype(str)
            .str.extract(pattern)[0]
            .astype(float)
            .fillna(0)
        )
    
    # ----------
    # Total
    # ----------
    df["status_total"] = df[[f"status_{k}" for k in keys]].sum(axis=1)

    # -----------------
    # Important ratios
    # -----------------
    df["status_engaged_ratio"] = (
        (df["status_beaten"] + df["status_playing"]) / df["status_total"]
    ).replace({np.inf: 0, np.nan: 0})

    df["status_completion_ratio"] = (
        df["status_beaten"] / df["status_total"]
    ).replace({np.inf: 0, np.nan: 0})

    df["status_abandon_ratio"] = (
        df["status_dropped"] / df["status_total"]
    ).replace({np.inf: 0, np.nan: 0})

    df["status_plan_to_play_ratio"] = (
        df["status_toplay"] / df["status_total"]
    ).replace({np.inf: 0, np.nan: 0})

    # --------------------------
    # Round ratio to 2 decimals
    # --------------------------
    df[[ 
        "status_engaged_ratio",
        "status_completion_ratio",
        "status_abandon_ratio",
        "status_plan_to_play_ratio"
    ]] = df[[ 
        "status_engaged_ratio",
        "status_completion_ratio",
        "status_abandon_ratio",
        "status_plan_to_play_ratio"
    ]].round(2)

    # --------------------------
    # Drop original column
    # --------------------------
    df = df.drop(columns=[col])

    return df


# =============================================================
# 3. Function to clean and expand the "platforms" columns
# # ===========================================================

def clean_platforms_column(df, col):
    # --------------------------------------
    # Extract the list of platform names
    # --------------------------------------
    df["platforms_list"] = df[col].astype(str).apply(
        lambda x: ", ".join(re.findall(r"'name': '([^']+)'", x))
    )

    # --------------------------------------
    # Number of platforms
    # --------------------------------------
    df["platforms_count"] = df["platforms_list"].apply(
        lambda x: len(x.split(", ")) if isinstance(x, str) and x else 0
    )

    # --------------------------------------
    # Drop original column
    # --------------------------------------
    df = df.drop(columns=[col])

    return df


# =============================================================
# 4. Function to clean and expand the "genres" column
# =============================================================

def clean_genres_column(df, col):
    # --------------------------------------
    # Extract the list of genre names
    # --------------------------------------
    df["genres_list"] = df[col].astype(str).apply(
        lambda x: ", ".join(re.findall(r"'name': '([^']+)'", x))
    )

    # --------------------------------------
    # Number of genres
    # --------------------------------------
    df["genres_count"] = df["genres_list"].apply(
        lambda x: len(x.split(", ")) if isinstance(x, str) and x else 0
    )

    # --------------------------------------
    # Drop original column
    # --------------------------------------
    df = df.drop(columns=[col])

    return df


# =============================================================
# 5. Function to clean and expand the "stores" column
# =============================================================

def clean_stores(df, col):
    # --------------------------------------
    # Extract stores names
    # --------------------------------------
    df["store_list"] = df[col].astype(str).apply(
        lambda x: ", ".join(re.findall(r"'name': '([^']+)'", x))
    )

    # --------------------------------------
    # Remove empty strings
    # --------------------------------------
    df["store_list"] = df["store_list"].apply(
        lambda x: x if x != "" else np.nan
    )

    # --------------------------------------
    # Number of stores
    # --------------------------------------
    df["store_count"] = df["store_list"].apply(
        lambda x: len(x.split(", ")) if isinstance(x, str) and x else 0
    )

    # --------------------------------------
    # Drop original column
    # --------------------------------------
    df = df.drop(columns=[col])

    return df


# =============================================================
# 6. Function to clean and expand the "tags" column
# =============================================================
def clean_tags_column(df, tags_col):
    
    def convert_to_list(x):
        if isinstance(x, list):
            return x
        if isinstance(x, str):
            # ----------------------------
            # Try JSON (most common case)
            # ----------------------------
            try:
                return json.loads(x)
            except:
                pass
            # ----------------------------
            # Try AST
            # ----------------------------
            try:
                return ast.literal_eval(x)
            except:
                return []
        return []

    df[tags_col] = df[tags_col].apply(convert_to_list)

    def extract_tags(tags):
        if not isinstance(tags, list):
            return []
        return [t.get("name", "").strip()
                for t in tags
                if isinstance(t, dict) and t.get("name")]

    df["tags_list"] = df[tags_col].apply(lambda x: ", ".join(extract_tags(x)))
    df["tags_count"] = df[tags_col].apply(lambda x: len(extract_tags(x)))

    df = df.drop(columns=[tags_col])
    
    return df


# =============================================================
# 7. Function to clean and expand the "esrb_rating" column
# =============================================================
def clean_esrb_column(df, col):
    # -------------------------
    # Extract ESRB rating name
    # -------------------------
    df["esrb_rating_list"] = df[col].astype(str).apply(
        lambda x: re.search(r"'name': '([^']+)'", x).group(1) if re.search(r"'name': '([^']+)'", x) else np.nan
    )

    # -------------------------
    # Drop original column
    # -------------------------
    df = df.drop(columns=[col])

    return df













