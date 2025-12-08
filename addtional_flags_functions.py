import pandas as pd
import re

# ====================================================================================================================
# 1. Additional function to create a platform flag dataframe (useful for ML models analysis and Hypothesis Testing)
# ====================================================================================================================

def create_platform_flags(df):
    # ----------------------------------
    # New dataframe with id + game name
    # ----------------------------------
    out = pd.DataFrame()
    out["rawg_id"] = df["rawg_id"]
    out["game_name"] = df["game_name"]

    # ----------------------------------
    # Source : platforms_list column
    # ----------------------------------
    pls = df["platforms_list"].astype(str)

    # ----------------------------------
    # Flags
    # ----------------------------------
    out["is_pc"] = pls.str.contains(r"\bPC\b", case=False, regex=True)
    out["is_playstation"] = pls.str.contains(r"PlayStation", case=False, regex=True)
    out["is_xbox"] = pls.str.contains(r"Xbox", case=False, regex=True)
    out["is_nintendo"] = pls.str.contains(r"Switch|Wii|GameCube|Nintendo|3DS", case=False, regex=True)
    out["is_mobile"] = pls.str.contains(r"iOS|Android", case=False, regex=True)

    # ----------------------------------
    # Convert to int (0/1)
    # ----------------------------------
    out = out.astype({
        "is_pc": int,
        "is_playstation": int,
        "is_xbox": int,
        "is_nintendo": int,
        "is_mobile": int
    })

    return out


# ==============================================================================================================
# 2. Additional function to create a genre flag dataframe (useful for ML models analysis and Hypothesis Testing
# ==============================================================================================================

def create_genre_flags(df):
    # ------------------------------------------------------------------
    # Extract the complete list of genres present in the entire dataset
    # ------------------------------------------------------------------
    all_genres = (
        df["genres_list"]
        .dropna()
        .apply(lambda x: x.split(", "))
        .explode()
        .str.strip()
        .unique()
    )

    all_genres = list(all_genres)
    all_genres.remove('')  # Remove empty string if present

    # --------------
    # New dataframe
    # --------------
    out = pd.DataFrame()
    out["rawg_id"] = df["rawg_id"]
    out["game_name"] = df["game_name"]

    # --------------------------
    # Initialize all flags to 0
    # --------------------------
    for genre in all_genres:
        colname = "is_" + genre.lower().replace(" ", "_")
        out[colname] = df["genres_list"].str.contains(genre, regex=False).astype(int)

    return out


# ==============================================================================================================
# 3. Additional function to create a store flag dataframe (useful for ML models analysis and Hypothesis Testing)
# ==============================================================================================================
def generate_store_indicators(df,
                              store_list_col,
                              id_col,
                              name_col):

    # ----------------------------------
    # Stores normalization function
    # ----------------------------------
    def normalize_store(store_name):
        s = store_name.lower()

        # --------------------------------
        # Xbox: multiple stores → one
        # --------------------------------
        if "xbox" in s:
            return "xbox_store"
        
        # --------------------------------
        # PlayStation: same
        # --------------------------------
        if "playstation" in s:
            return "playstation_store"

        # ----------------------------------
        # General normalization
        # ----------------------------------
        s = re.sub(r"[^a-z0-9]+", "_", s)
        return s.strip("_")

    # ----------------------------------
    # Extract unique stores
    # ----------------------------------
    all_stores = set()

    for stores in df[store_list_col]:
        if isinstance(stores, str) and stores.strip():
            for s in stores.split(", "):
                all_stores.add(normalize_store(s.strip()))

    # ----------------------------------
    # New dataset
    # ----------------------------------
    result = df[[id_col, name_col]].copy()

    # ----------------------------------
    # Create columns
    # ----------------------------------
    for s in all_stores:
        result[f"store_{s}"] = 0

    # ----------------------------------
    # Fill columns
    # ----------------------------------
    for idx, row in df.iterrows():
        if isinstance(row[store_list_col], str):
            for s in row[store_list_col].split(", "):
                col = "store_" + normalize_store(s.strip())
                result.at[idx, col] = 1

    return result

# ========================================================================================================================
# 4. Additional functions to create a multi-platform flag dataframe (useful for ML models analysis and Hypothesis Testing)
# ========================================================================================================================
def create_multi_platform_flag(df):
    # ----------------------------------
    # New dataframe with id + game name
    # ----------------------------------
    out = pd.DataFrame()
    out["rawg_id"] = df["rawg_id"]
    out["game_name"] = df["game_name"]

    # ----------------------------------
    # Source : platforms_list column
    # ----------------------------------
    pls = df["platforms_list"].astype(str)

    # ----------------------------------
    # Multi-platform flag
    # ----------------------------------
    out["is_multi_platform"] = pls.apply(lambda x: 1 if len(x.split(", ")) > 1 else 0)

    return out


# ====================================================================================================================
# 5. Additional function to create a high rating flag dataframe (useful for ML models analysis and Hypothesis Testing)
# ====================================================================================================================
def create_high_rating_flag(df):
    # ----------------------------------
    # New dataframe with id + game name
    # ----------------------------------
    out = pd.DataFrame()
    out["rawg_id"] = df["rawg_id"]
    out["game_name"] = df["game_name"]
    # ----------------------------------
    # Source : users_rating column
    # ----------------------------------
    rat = df["user_rating"].astype(float)

    # ----------------------------------
    # High rating flag
    # ----------------------------------
    out["is_high_rating"] = rat.apply(lambda x: 1 if x >= 4.0 else 0)

    return out


# ========================================================================================================================
# 6. Additional function to create a multiplayer tag flag dataframe (useful for ML models analysis and Hypothesis Testing)
# ========================================================================================================================
def create_multiplayer_flag(df, id_col, name_col, tags_col):
    # ----------------------------------------------
    # Multiplayer key-words to detect
    # ----------------------------------------------
    multiplayer_keywords = [
        "multiplayer", "online", "co-op", "co op", "coop", "fps", "cooperative",
        "mmo", "pvp", "pve", "crossplay", "lan", "battle-royale", "battle royale",
        "survival-multiplayer"
    ]

    # ----------------------------------------------------------
    # Build a robust unique regex (lowercase + full word search)
    # ----------------------------------------------------------
    pattern = r"|".join([re.escape(k.lower()) for k in multiplayer_keywords])

    # -----------------------------------------
    # Normalize the tags_list field (as string)
    # -----------------------------------------
    df["tags_list_norm"] = df[tags_col].astype(str).str.lower()

    # ------------------------
    # Create the binary flag
    # ------------------------
    df["is_multiplayer"] = df["tags_list_norm"].str.contains(pattern, regex=True).astype(int)

    # ----------------------
    # New final dataframe
    # ----------------------
    tag_multiplayer = df[[id_col, name_col, "is_multiplayer"]].copy()

    # --------
    # Cleanup
    # --------
    df.drop(columns=["tags_list_norm"], inplace=True)

    return tag_multiplayer


# =======================================================================
# Additional function to normalize tags
# =======================================================================
# def normalize_tag(slug):
#     s = slug.lower()

#     # Example of regroupments
#     if s in ["cooperative", "coop", "co-op"]:
#         return "co_op"

#     if s in ["singleplayer", "single-player"]:
#         return "singleplayer"

#     if s in ["multiplayer", "multi-player"]:
#         return "multiplayer"

#     # General cleaning
#     s = re.sub(r"[^a-z0-9]+", "_", s)
#     return s.strip("_")


# =======================================================================
# Additional function to create a tag indicators dataframe (useful for ML models analysis and Database creation)
# =======================================================================
# def generate_tag_indicators(df,
#                             tags_list_col,
#                             id_col,
#                             name_col):

#     # Retrieve all tags
#     all_tags = set()
#     for tag_string in df[tags_list_col]:
#         if isinstance(tag_string, str) and tag_string.strip():
#             for t in tag_string.split(", "):
#                 all_tags.add(normalize_tag(t))

#     # New dataframe
#     result = df[[id_col, name_col]].copy()

#     # Add columns
#     for t in sorted(all_tags):
#         result[f"tag_{t}"] = 0

#     # 3. Filling columns
#     for idx, row in df.iterrows():
#         if isinstance(row[tags_list_col], str):
#             for t in row[tags_list_col].split(", "):
#                 col = "tag_" + normalize_tag(t)
#                 result.at[idx, col] = 1

#     return result


# ----------------------------------------------------------------------
# Additional function to create ESRB rating indicators dataframe
# ----------------------------------------------------------------------
# def generate_esrb_indicators(df,
#                              esrb_col,
#                              id_col,
#                              name_col):

#     # Retrieve all ESRB ratings
#     all_ratings = df[esrb_col].dropna().unique()

#     # New dataframe
#     result = df[[id_col, name_col]].copy()

#     # Add columns
#     for rating in all_ratings:
#         colname = "esrb_" + normalize_tag(rating)
#         result[colname] = (df[esrb_col] == rating).astype(int)

#     return result