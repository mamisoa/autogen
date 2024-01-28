from holidays import Country, bunch

BE = Country('BE')
print("Belgian Bank Holidays in 2023:")
for holiday in BE.holidays(years=range(2023, 2025)):
    print(f"{holiday.name}: {holiday.date}")
