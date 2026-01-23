"""Test script to find correct AKShare API names."""

import akshare as ak

print(f"AKShare version: {ak.__version__}")
print("\nAvailable fund-related functions:")

# List all fund-related attributes
fund_attrs = [attr for attr in dir(ak) if 'fund' in attr.lower()]
for attr in sorted(fund_attrs)[:30]:  # Show first 30
    print(f"  - {attr}")

print("\n\nTrying to fetch fund list...")

# Try different function names
functions_to_try = [
    "fund_open_fund_info_em",
    "fund_em_fund_name",
    "fund_name_em",
    "fund_em_open_fund_info_name",
    "fund_open_fund_rank_em",
]

for func_name in functions_to_try:
    try:
        func = getattr(ak, func_name, None)
        if func:
            print(f"\n✓ Found: {func_name}")
            result = func()
            if hasattr(result, 'head'):
                print(f"  Columns: {list(result.columns)[:5]}")
                print(f"  Shape: {result.shape}")
                print(f"  First row:\n{result.head(1)}")
            break
    except Exception as e:
        print(f"✗ {func_name}: {e}")
