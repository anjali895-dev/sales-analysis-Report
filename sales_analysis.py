# =============================================================================
# SALES ANALYSIS AND PERFORMANCE REPORT - September 2024
# Cell-by-cell code. Run one cell at a time (VS Code: "Run Cell" above each
# "# %%"; Jupyter: copy each block into its own cell).
# One-time install:  pip install pandas openpyxl python-calamine matplotlib
# =============================================================================

# %% CELL 1: Load both files and combine them  (your own code, unchanged)
import pandas as pd

path_1 = "data/Sep part 1.xlsx"      # put the raw file here (not included in the repo)
path_2 = "data/Sep part 2.xlsx"

a = pd.read_excel(path_1, engine="calamine")
b = pd.read_excel(path_2, engine="calamine")

df = pd.concat([a, b], ignore_index=True)
df["date"] = pd.to_datetime(df["date"])

total_sales = df["total"].sum()
invoices    = df["invoice_no"].nunique()
orders      = df["order_id"].nunique()
aiv         = total_sales / invoices
aov         = total_sales / orders

state = df.groupby("customer_state").agg(
    sales=("total","sum"), invoices=("invoice_no","nunique"),
    customers=("customer_id","nunique"), reps=("hesaathi_code","nunique"))
state["share"] = state["sales"] / total_sales
state = state.sort_values("sales", ascending=False)

# %% CELL 2: Check the combined data (rows, duplicates, dates)
print("Part 1 rows :", f"{len(a):,}")
print("Part 2 rows :", f"{len(b):,}")
print("Combined    :", f"{len(df):,}")
print("Same columns in both files:", list(a.columns) == list(b.columns))
print("Fully duplicated rows     :", df.duplicated().sum())
print("Repeated serial_numbers   :", df["serial_numbers"].duplicated().sum())
print("Date range                :", df["date"].min().date(), "to", df["date"].max().date())
print("Currencies                :", df["currency"].unique().tolist())
missing = df.isna().sum()
print("Columns with missing values:\n", missing[missing > 0])

# %% CELL 3: Clean the category spellings
CATEGORY_FIX = {
    "Stapes and Essentials": "Staples and Essentials",
    "Staples and Esstentials": "Staples and Essentials",
    "Spices, Masalas & Condiments": "Spices, Masalas, and Condiments",
    "Spices,Masalas and Condiments": "Spices, Masalas, and Condiments",
    "Snacks and Namkeen": "Snacks and Namkeens",
    "Bakery and Confectionary": "Bakery and Confectionery",
    "Stationery and Office Supplies": "Stationery & Office Supplies",
    "Dried Fruits and Nuts": "Dry Fruits and Nuts",
    "FNV": "FNV - Fruits & Vegetables",
}
print("Categories before:", df["category"].nunique())
df["category"] = df["category"].replace(CATEGORY_FIX)
print("Categories after :", df["category"].nunique())

# %% CELL 4: A reusable group-by function (use it for any column)
def summarize(data, by):
    """sales, invoices, customers, reps, share, avg invoice, rank, cumulative share"""
    out = data.groupby(by).agg(
        sales=("total", "sum"),
        invoices=("invoice_no", "nunique"),
        lines=("total", "size"),
        customers=("customer_id", "nunique"),
        reps=("hesaathi_code", "nunique"),
    )
    out["share"] = out["sales"] / data["total"].sum()
    out["avg_invoice"] = out["sales"] / out["invoices"]
    out = out.sort_values("sales", ascending=False)
    out["cum_share"] = out["share"].cumsum()
    out["rank"] = range(1, len(out) + 1)
    return out

# %% CELL 5: Overall KPIs
CRORE = 10_000_000
invoice_values = df.groupby("invoice_no")["total"].sum()
order_values   = df.groupby("order_id")["total"].sum()

kpis = pd.DataFrame({
    "Metric": ["Total sales (Rs)", "Total sales (Rs Cr)", "Taxable value (Rs)", "Total invoices",
               "Total orders", "Invoice lines", "Unique customers", "Sales reps", "Products",
               "Districts", "Average sales per line (Rs)", "Average invoice value (Rs)",
               "Median invoice value (Rs)", "AOV per order (Rs)", "Median order value (Rs)",
               "Average daily sales (Rs Cr)"],
    "Value": [total_sales, total_sales / CRORE, df["taxable_value"].sum(), invoices, orders,
              len(df), df["customer_id"].nunique(), df["hesaathi_code"].nunique(),
              df["product_name"].nunique(),
              df.groupby(["customer_state", "customer_district"]).ngroups,
              total_sales / len(df), aiv, invoice_values.median(), aov, order_values.median(),
              total_sales / CRORE / df["date"].nunique()],
})
print(kpis.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))

# %% CELL 6: Business lines (entity and sub-vertical)
entity       = summarize(df, "facilitator")
vertical     = summarize(df, "vertical")
sub_vertical = summarize(df, "sub_vertical")
print(sub_vertical[["sales", "share", "invoices", "avg_invoice"]].round(3))

# %% CELL 7: Geography - states, state x business line, districts
state = summarize(df, "customer_state")
state["sales_per_rep"]      = state["sales"] / state["reps"]
state["sales_per_customer"] = state["sales"] / state["customers"]
print(state[["sales", "share", "invoices", "avg_invoice", "reps", "sales_per_rep"]].round(3))

state_vertical = df.pivot_table(index="customer_state", columns="vertical",
                                values="total", aggfunc="sum").fillna(0)
print(state_vertical.round(0))

district = summarize(df, ["customer_state", "customer_district"])
print("\nTop 10 districts:\n", district.head(10)[["sales", "share", "invoices", "avg_invoice"]].round(3))
print("\nWeakest 10 districts:\n", district.sort_values("sales").head(10)[["sales", "invoices", "reps"]])
print("\nTop 10 districts share:", round(district["share"].head(10).sum(), 3))
print("Top 20 districts share:", round(district["share"].head(20).sum(), 3))

# %% CELL 8: Sales reps - ranking, bands, concentration
rep = summarize(df, "hesaathi_code")
rep["state"] = df.groupby("hesaathi_code")["customer_state"].agg(lambda s: s.mode()[0])
print(rep.head(10)[["state", "sales", "share", "invoices", "customers", "avg_invoice"]].round(3))

bins   = [0, 5_000, 10_000, 25_000, 50_000, 100_000, 500_000, float("inf")]
labels = ["Up to 5k", "5-10k", "10-25k", "25-50k", "50k-1 lakh", "1-5 lakh", "Above 5 lakh"]
rep["band"] = pd.cut(rep["sales"], bins=bins, labels=labels)
rep_bands = rep.groupby("band", observed=False).agg(reps=("sales", "size"), sales=("sales", "sum"))
rep_bands["share_of_reps"]  = rep_bands["reps"]  / rep_bands["reps"].sum()
rep_bands["share_of_sales"] = rep_bands["sales"] / rep_bands["sales"].sum()
print("\n", rep_bands.round(3))

s, n = rep["sales"].sort_values(ascending=False), len(rep)
print("\nTop 10 reps share   :", round(s.head(10).sum() / s.sum(), 3))
print("Top 1% reps share   :", round(s.head(int(n * 0.01)).sum() / s.sum(), 3))
print("Top 10% reps share  :", round(s.head(int(n * 0.10)).sum() / s.sum(), 3))
print("Bottom 50% share    :", round(s.tail(n // 2).sum() / s.sum(), 3))
print("Reps below Rs 10,000:", int((rep["sales"] < 10_000).sum()))

# %% CELL 9: Products and categories
product  = summarize(df, "product_name")
category = summarize(df, "category")
print(product.head(10)[["sales", "share", "cum_share", "invoices"]].round(3))
print("\nProducts needed for 80% revenue:", int((product["cum_share"] < 0.80).sum() + 1))
print("Products under Rs 10,000 total :", int((product["sales"] < 10_000).sum()))
print("\nMost frequent products:\n", product.sort_values("invoices", ascending=False).head(10)[["invoices", "sales"]])
print("\nLowest 15 products:\n", product.sort_values("sales").head(15)[["sales", "lines"]])
print("\nTop categories:\n", category.head(10)[["sales", "share", "cum_share"]].round(3))

# %% CELL 10: Invoice analysis (value bands, largest invoices)
inv = df.groupby("invoice_no").agg(total=("total", "sum"), date=("date", "first"),
                                   state=("customer_state", "first"))
bins   = [0, 100, 250, 500, 1_000, 2_500, 5_000, 10_000, 50_000, float("inf")]
labels = ["Up to 100", "100-250", "250-500", "500-1,000", "1,000-2,500",
          "2,500-5,000", "5,000-10,000", "10,000-50,000", "Above 50,000"]
inv["band"] = pd.cut(inv["total"], bins=bins, labels=labels)
inv_bands = inv.groupby("band", observed=False).agg(invoices=("total", "size"), sales=("total", "sum"))
inv_bands["pct_invoices"] = inv_bands["invoices"] / inv_bands["invoices"].sum()
inv_bands["pct_sales"]    = inv_bands["sales"]    / inv_bands["sales"].sum()
inv_bands["avg_invoice"]  = inv_bands["sales"] / inv_bands["invoices"]
print(inv_bands.round(3))
print("\nLargest 10 invoices:\n", inv.sort_values("total", ascending=False).head(10))

# %% CELL 11: Daily, weekly and hourly trend
daily = df.groupby("date").agg(sales=("total", "sum"), invoices=("invoice_no", "nunique"))
daily["avg_invoice"] = daily["sales"] / daily["invoices"]
daily["weekday"] = daily.index.day_name()
daily["week"]    = (daily.index.day - 1) // 7 + 1
weekly = daily.groupby("week").agg(sales=("sales", "sum"), invoices=("invoices", "sum"))
hourly = df.groupby(df["date_time"].dt.hour).agg(sales=("total", "sum"), invoices=("invoice_no", "nunique"))
print(daily.round(0).head(), "\n\n", weekly.round(0), "\n\n", hourly.round(0))

# %% CELL 12: Charts (saved as PNG)
import os
import matplotlib.pyplot as plt
OUT = "output"
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False})

fig, ax = plt.subplots(figsize=(8, 4))
v = state["sales"].sort_values() / CRORE
ax.barh(v.index, v.values, color="#2F5597"); ax.set_title("Sales by state (Rs Cr)")
for i, x in enumerate(v.values): ax.text(x, i, f" {x:,.1f}", va="center")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "chart_state_sales.png"), dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4.5))
v = (product["sales"].head(10) / CRORE).iloc[::-1]
ax.barh(v.index, v.values, color="#2F5597"); ax.set_title("Top 10 products (Rs Cr)")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "chart_top_products.png"), dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4)); x = range(len(inv_bands))
ax.bar([i - .2 for i in x], inv_bands["pct_invoices"] * 100, .4, label="% of invoices", color="#A6A6A6")
ax.bar([i + .2 for i in x], inv_bands["pct_sales"] * 100, .4, label="% of sales", color="#2F5597")
ax.set_xticks(list(x)); ax.set_xticklabels(inv_bands.index, rotation=30, ha="right")
ax.legend(); ax.set_title("Invoices vs sales by invoice value (Rs)")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "chart_invoice_bands.png"), dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(daily.index, daily["sales"] / CRORE, marker="o", color="#2F5597")
ax.axhline(daily["sales"].mean() / CRORE, ls="--", color="grey", label="Average")
ax.set_title("Daily sales (Rs Cr)"); ax.legend(); fig.autofmt_xdate(); fig.tight_layout()
fig.savefig(os.path.join(OUT, "chart_daily_sales.png"), dpi=150); plt.close(fig)
print("Charts saved in:", OUT)

# %% CELL 13: Export small tables for Power BI (one Excel file)
def flat(t, **kw):               # index -> normal column, so Power BI can read it
    return t.reset_index(**kw)

inv_bands_pbi = flat(inv_bands); inv_bands_pbi["band_order"] = range(1, len(inv_bands_pbi) + 1)
rep_bands_pbi = flat(rep_bands); rep_bands_pbi["band_order"] = range(1, len(rep_bands_pbi) + 1)
daily_pbi = flat(daily); daily_pbi["weekday_num"] = daily_pbi["date"].dt.dayofweek + 1      # Monday = 1 (for sorting in Power BI)
daily_pbi["date"] = daily_pbi["date"].dt.date
sv_long = state_vertical.stack().reset_index(); sv_long.columns = ["customer_state", "vertical", "sales"]
rep_top = rep.head(100).reset_index()
rep_top["band"] = rep_top["band"].astype(str)

with pd.ExcelWriter(os.path.join(OUT, "PowerBI_Data.xlsx")) as w:
    kpis.to_excel(w, sheet_name="KPIs", index=False)
    flat(entity).to_excel(w, sheet_name="Entity", index=False)
    flat(sub_vertical).to_excel(w, sheet_name="SubVertical", index=False)
    flat(state).to_excel(w, sheet_name="State", index=False)
    sv_long.to_excel(w, sheet_name="State_Vertical", index=False)
    flat(district).to_excel(w, sheet_name="District", index=False)
    rep_top.to_excel(w, sheet_name="Rep_Top100", index=False)
    rep_bands_pbi.to_excel(w, sheet_name="Rep_Bands", index=False)
    flat(product).to_excel(w, sheet_name="Product", index=False)
    flat(category).to_excel(w, sheet_name="Category", index=False)
    inv_bands_pbi.to_excel(w, sheet_name="Invoice_Bands", index=False)
    daily_pbi.to_excel(w, sheet_name="Daily", index=False)
    flat(hourly).rename(columns={"date_time": "hour"}).to_excel(w, sheet_name="Hourly", index=False)
print("Power BI file saved:", os.path.join(OUT, "PowerBI_Data.xlsx"))
