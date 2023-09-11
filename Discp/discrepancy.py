import pandas as pd

def get_discrepancies(road_name):
    # Load CSV files into DataFrames
    merged_data = pd.read_csv(f'unified/{road_name}.csv')

    # Perform comparative analysis
    def compare_values(row):
        # Check if measurements match within a tolerance
        tolerance = 0.6
        return abs(row[' Values_csv1'] - row[' Values_csv2']) <= tolerance and \
               abs(row[' Values_csv2'] - row[' Values']) <= tolerance

    merged_data['Match'] = merged_data.apply(compare_values, axis=1)

    # Print discrepancies
    discrepancies = merged_data[merged_data['Match'] == False]
    # print("Discrepancies:")
    # print(discrepancies)
    discrepancies.to_csv('Discrepancies.csv', index=False)

get_discrepancies("road_1")