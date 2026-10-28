Place the two raw sales files here to run the code:

- `Sep part 1.xlsx`
- `Sep part 2.xlsx`

The raw data is confidential and is not included in this repository.

# Sales Analysis and Performance Report: September 2024

Analysis of one month of sales data (about 19.2 lakh invoice lines) to understand where sales come from, what is under-performing, and how to improve. Built with Python (pandas), Excel and Power BI.

## Key findings

- Total sales: **Rs 135.02 Cr** across 7.8 lakh invoices; average invoice Rs 1,732; AOV (per order) Rs 2,521
- **Telangana** contributes 44.5% of sales; the top 10 districts contribute 59.5%
- The **top 1% of sales reps** make 35% of sales; the bottom half make under 4%
- Only **3.9% of invoices** (above Rs 10,000) bring 53.7% of revenue; half of all invoices are under Rs 250
- **68 of 958 products** generate 80% of revenue

## What is in this repository

| Folder | Contents |
|---|---|
| `report/` | Final Excel report: overview, geography, performance, products, invoices, insights, recommendations, assumptions |
| `code/` | Python script (`sales_analysis.py`), written as cells that can be run one by one |
| `powerbi/` | `PowerBI_Data.xlsx`: summary tables used by the Power BI dashboard |
| `data/` | Empty on purpose: raw data is confidential and not uploaded |

## Approach

1. Combined the two source files (same structure) and checked for duplicates and missing values
2. Cleaned category spelling variants (52 names became 43)
3. Grouped the data by state, district, sales rep, product, category and invoice
4. Calculated KPIs, rankings, share of sales and Pareto (80/20) analysis
5. Built the Excel report and a 5-page Power BI dashboard
6. Wrote insights and recommendations backed by the numbers

## How to run

```
pip install -r requirements.txt
python code/sales_analysis.py      # or run the file cell by cell in VS Code / Jupyter
```

Put the two raw files in the `data/` folder first. The first run is slow (large files); results are written to an `output/` folder.

## Dashboard walkthrough

Video: **["C:\Users\lenovo\Videos\Data_Analysis_Report1.mp4"]**

## Limitations

- Only one month of data, so trends over time could not be tested
- No cost or margin data, so recommendations are based on revenue, not profit
- Quantities are in mixed units, so products are ranked by revenue and invoice count
- Sales rep is assumed to be the `hesaathi_code` field

## Author

Anjali | [[LinkedIn profile link](https://www.linkedin.com/in/anjali-sharma-34bb8b143)] | [anjali8959@gmail.com]
