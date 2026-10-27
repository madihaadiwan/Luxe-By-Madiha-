# 👗 Luxe by Madiha - Sales Dashboard (Streamlit)

Interactive sales analysis for an online store selling Khaadi original dresses.
**The bundled orders are SAMPLE (fake) data** (600 orders + deliberate mess) so you can practise. Replace them with real orders before submitting.

## Quick start
```bash
./run.sh        # macOS / Linux          run.bat   # Windows
```
or: `pip install -r requirements.txt` then `streamlit run app.py` (Python 3.9+). Opens at http://localhost:8501

## Use your real data
1. Open `data/Luxe_Orders.xlsx` and replace the rows with your orders, keeping these columns:
   `OrderID, Date, Product, Category, Price, Discount, City, Payment, Status, Source`
   (Discount as a fraction, e.g. 0.10 for 10%; Status = Delivered / Returned / Cancelled; no customer names or phone numbers).
2. Run the app again. Everything, including the cleaning log, updates. Optional: `python clean_and_export.py` writes the cleaned CSV.
3. `python generate_sample_data.py` recreates the sample file (it overwrites `Luxe_Orders.xlsx`).

## Structure
`app.py` (layout, filters, tabs) · `utils/data_cleaning.py` (cleaning + features + validation) · `clean_and_export.py` · `generate_sample_data.py` · `data/`

## Cleaning performed (on the sample data)
Duplicate orders removed, city typos/case fixed, 'Cash on Delivery' merged into COD, status case fixed, missing City -> 'Unknown', missing Discount -> 0%.
Features added: NetPrice, Revenue (delivered orders only), ReturnFlag, CancelFlag, Month, Weekday, DiscountBand.

## Tabs
Overview (KPIs, auto insights) · Products · Seasonality · Customers · Returns & payments · Data & quality (cleaning log, explorer, downloads).
Sidebar filters: category, city, payment, source, date range.

> Rates and patterns are descriptive, not causal. Small groups give unreliable percentages.
"# Luxe-By-Madiha-" 
