"""Creates SAMPLE (fake) raw order data with realistic mess, for practice only.
Replace data/Luxe_Orders.xlsx with your real orders (same columns) and everything else updates."""
import datetime as dt
from pathlib import Path
import numpy as np, pandas as pd
rng = np.random.default_rng(42)
CATS = {"Lawn 3-Piece": (5500, 9500, ["Printed Lawn Suit", "Embroidered Lawn Suit", "Digital Print Lawn"]),
        "Winter Khaddar": (6500, 12000, ["Khaddar Embroidered Suit", "Karandi 3-Piece", "Winter Printed Suit"]),
        "Formal / Chiffon": (12000, 28000, ["Chiffon Formal Suit", "Wedding Formal 3-Piece", "Net Embroidered Suit"]),
        "Ready-to-Wear": (3500, 7500, ["Pret Kurta Set", "Co-ord Set", "Printed Pret 2-Piece"]),
        "Kurti": (2500, 4500, ["Cotton Kurti", "Embroidered Kurti", "Printed Kurti"])}
CITIES = ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Multan", "Hyderabad", "Peshawar", "Other"]
CW = np.array([30, 22, 10, 7, 7, 6, 5, 4, 9], float); CW /= CW.sum()
MW = [1.0, 1.1, .7, .8, 1.6, 1.3, 1.5, 1.0, .8, 1.0, .9, 1.1]  # Nov 2025 .. Oct 2026
MONTHS = [(2025, 11), (2025, 12)] + [(2026, m) for m in range(1, 11)]

def cat_w(m):
    w = np.array([3.0 if m in (3, 4, 5, 6, 7, 8) else .4, 3.0 if m in (10, 11, 12, 1, 2) else .2,
                  2.5 if m in (11, 12, 3, 5) else 1.0, 2.0, 1.5]); return w / w.sum()

rows = []
for i in range(600):
    y, m = MONTHS[rng.choice(12, p=np.array(MW) / sum(MW))]
    d = dt.date(y, m, int(rng.integers(1, 29)))
    c = str(rng.choice(list(CATS), p=cat_w(m))); lo, hi, names = CATS[c]
    sale = m in (7, 8, 1)
    disc = float(rng.choice([0, .05, .10, .15, .20, .30], p=[.2, .1, .2, .2, .2, .1] if sale else [.6, .15, .15, .07, .03, 0]))
    pay = str(rng.choice(["COD", "Bank Transfer", "Easypaisa/JazzCash"], p=[.68, .2, .12]))
    pr = (.13 if pay == "COD" else .05) + (.03 if disc >= .2 else 0); pc = .09 if pay == "COD" else .02; u = rng.random()
    rows.append([d, str(rng.choice(names)), c, int(round(rng.uniform(lo, hi) / 100) * 100), disc,
                 str(rng.choice(CITIES, p=CW)), pay, "Returned" if u < pr else "Cancelled" if u < pr + pc else "Delivered",
                 str(rng.choice(["Instagram", "WhatsApp", "Facebook", "Referral"], p=[.42, .30, .18, .10]))])
rows.sort(key=lambda r: r[0])
df = pd.DataFrame(rows, columns=["Date", "Product", "Category", "Price", "Discount", "City", "Payment", "Status", "Source"])
df.insert(0, "OrderID", [f"LM-{1001 + i}" for i in range(len(df))])
# ---- add realistic mess (so the cleaning step has something to do)
df["Date"] = df["Date"].astype(object)
for i in rng.choice(len(df), 14, replace=False): df.loc[i, "City"] = str(df.loc[i, "City"]).lower() + " "
for i in rng.choice(len(df), 8, replace=False): df.loc[i, "City"] = "Karchi"
for i in rng.choice(len(df), 20, replace=False): df.loc[i, "Payment"] = "Cash on Delivery"
for i in rng.choice(len(df), 12, replace=False): df.loc[i, "Status"] = str(df.loc[i, "Status"]).lower()
for i in rng.choice(len(df), 15, replace=False): df.loc[i, "City"] = np.nan
for i in rng.choice(len(df), 6, replace=False): df.loc[i, "Discount"] = np.nan
df = pd.concat([df, df.sample(9, random_state=1)], ignore_index=True).sample(frac=1, random_state=3).reset_index(drop=True)
df.to_excel(Path(__file__).parent / "data" / "Luxe_Orders.xlsx", index=False)
print("Sample raw data:", df.shape)
