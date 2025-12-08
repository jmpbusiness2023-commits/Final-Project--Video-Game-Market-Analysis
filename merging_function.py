import pandas as pd

def merge_games_data(df_games_list, df_games_details):

    # ===============================
    # 1) NON DESTRUCTIVE MERGE
    # ===============================

    df = df_games_list.merge(
        df_games_details,
        on="rawg_id",
        how="left",
        suffixes=("", "_det")
    )


    # ===================================
    # 2) COLUMNS TO COMBINE INTELLIGENTLY
    # ===================================

    cols_to_merge = [
        "tags_list", "tags_count",
        "genres_list", "genres_count",
        "platform_list", "platform_count",
        "esrb_rating_list",
        "released",
        "name"
    ]

    # ----------------------------------------------------------------------
    # Internal function: keep main version, replace NaN with details version
    # ----------------------------------------------------------------------
    def smart_combine(df, col):
        det_col = col + "_det"
        if det_col in df.columns:
            df[col] = df[col].fillna(df[det_col])
            df.drop(columns=[det_col], inplace=True)

    # ----------------------------------------------------------------------
    # Apply to all columns in the list
    # ----------------------------------------------------------------------
    for col in cols_to_merge:
        smart_combine(df, col)


    # ===============================
    # 3) ADD DEVELOPERS / PUBLISHERS
    # ===============================

    if "developers" in df.columns:
        df["developers"] = df["developers"].fillna("")
    if "publishers" in df.columns:
        df["publishers"] = df["publishers"].fillna("")


    # ===============================================
    # 4) DROP REMAINING "_det" COLUMNS (just in case)
    # ===============================================

    cols_to_drop = [c for c in df.columns if c.endswith("_det")]
    if cols_to_drop:
        df.drop(columns=cols_to_drop, inplace=True)

    # ===============================================
    # 5) RESET INDEX PROPERLY
    # ===============================================
    df.reset_index(drop=True, inplace=True)

    return df
