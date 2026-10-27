"""Load + clean Luxe by Madiha order data. Every step is logged so the dashboard can show it."""
from __future__ import annotations
from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "Luxe_Orders.xlsx"
CITY_FIX = {"karchi": "Karachi", "lhr": "Lahore", "isb": "Islamabad", "pindi": "Rawalpindi"}
PAY_FIX = {"cash on delivery": "COD", "cod": "COD", "bank transfer": "Bank Transfer",
           "easypaisa/jazzcash": "Easypaisa/JazzCash", "easypaisa": "Easypaisa/JazzCash", "jazzcash": "Easypaisa/JazzCash"}
BAND_ORDER = ["No discount", "1-10%", "11-20%", "Over 20%"]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def load_raw(path: Path | str = DATA_PATH) -> pd.DataFrame:
    return pd.read_excel(path)

def clean_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    df, log = raw.copy(), []
    add = lambda s, i, a, n: log.append({"Step": s, "Issue found": i, "Action taken": a, "Affected": n})
    for c in ["OrderID", "Product", "Category", "City", "Payment", "Status", "Source"]:
        df[c] = df[c].astype("string").str.strip()
    n = int(df.duplicated().sum()); df = df.drop_duplicates()
    add("Remove duplicates", "Fully identical order rows", "Dropped, kept first occurrence", f"{n} rows")
    n = int(df["OrderID"].duplicated().sum()); df = df.drop_duplicates(subset="OrderID", keep="first")
    add("Remove duplicates", "Same OrderID repeated", "Kept first record per OrderID", f"{n} rows")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    n = int(df["Date"].isna().sum()); df = df.dropna(subset=["Date"])
    add("Fix dates", "Unreadable or missing order dates", "Dropped (cannot place in time)", f"{n} rows")
    before = df["City"].copy()
    low = df["City"].str.lower()
    df["City"] = low.map(CITY_FIX).fillna(df["City"].str.title())
    n = int((before.notna() & (before != df["City"])).sum())
    add("Standardise categories", "City in lower case or misspelt (e.g. 'Karchi')", "Title-cased and mapped to the correct name", f"{n} rows")
    before = df["Payment"].copy()
    df["Payment"] = df["Payment"].str.lower().map(PAY_FIX).fillna(df["Payment"])
    add("Standardise categories", "Payment written as 'Cash on Delivery'", "Merged into 'COD'", f"{int((before != df['Payment']).sum())} rows")
    before = df["Status"].copy(); df["Status"] = df["Status"].str.title()
    add("Standardise categories", "Status in lower case ('delivered')", "Title-cased", f"{int((before != df['Status']).sum())} rows")
    n = int(df["City"].isna().sum()); df["City"] = df["City"].fillna("Unknown")
    add("Handle missing values", "Missing City", "Filled with 'Unknown' (rows kept)", f"{n} rows")
    n = int(df["Discount"].isna().sum()); df["Discount"] = df["Discount"].fillna(0.0).astype(float)
    add("Handle missing values", "Missing Discount", "Assumed no discount (0%)", f"{n} rows")
    df["Price"] = df["Price"].astype(float)
    for c in ["OrderID", "Product", "Category", "City", "Payment", "Status", "Source"]:
        df[c] = df[c].astype(str)
    df["NetPrice"] = df["Price"] * (1 - df["Discount"])
    df["Delivered"] = (df["Status"] == "Delivered").astype(int)
    df["ReturnFlag"] = (df["Status"] == "Returned").astype(int)
    df["CancelFlag"] = (df["Status"] == "Cancelled").astype(int)
    df["Revenue"] = df["NetPrice"] * df["Delivered"]
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    df["Weekday"] = df["Date"].dt.day_name()
    df["DiscountBand"] = pd.cut(df["Discount"], [-1, 0, .10, .20, 1], labels=BAND_ORDER).astype(str)
    add("Feature engineering", "Raw columns not directly analysable",
        "Added NetPrice, Revenue (delivered only), ReturnFlag, CancelFlag, Month, Weekday, DiscountBand", "7 new cols")
    assert df["OrderID"].is_unique and (df["Price"] > 0).all()  # validation on every load
    return df.sort_values("Date").reset_index(drop=True), log
