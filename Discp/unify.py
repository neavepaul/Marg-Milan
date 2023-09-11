import pandas as pd

def unify_files(road_name):
    # Load CSV files into DataFrames
    csv1 = pd.read_csv(f'{road_name}/csv1.csv')
    csv2 = pd.read_csv(f'{road_name}/csv2.csv')
    csv3 = pd.read_csv(f'{road_name}/csv3.csv')

    csv1['Index'] = range(len(csv1))
    csv2['Index'] = range(len(csv2))
    csv3['Index'] = range(len(csv3))

    merged_data = pd.merge(csv1, csv2, on=['Index', 'Test_name'], suffixes=('_qcr1', '_qcr2'))
    merged_data = pd.merge(merged_data, csv3, on=['Test_name', 'Index'])
    merged_data = merged_data.drop(['Index'], axis=1)
    merged_data['road_id'] = [road_name]*len(merged_data)
    merged_data.rename(columns = {'Test_no':'Subtest_qmr', 'Values': 'Values_qmr', 'Test_no_qcr1': 'Subtest_qcr1', 'Test_no_qcr2': 'Subtest_qcr2'}, inplace = True)

    merged_data.to_csv(f'unified/{road_name}.csv', index=False)

unify_files("road_1")