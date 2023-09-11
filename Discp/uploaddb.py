import pandas as pd
from sqlalchemy import create_engine

road_name = "road_1"
# Replace these with your PostgreSQL database credentials
db_username = 'postgres'
db_password = 'neave'
db_host = 'localhost:5432'
db_name = 'SIH'

# Create a connection string
connection_string = f"postgresql://{db_username}:{db_password}@{db_host}/{db_name}"

merged_data = pd.read_csv(f'unified/{road_name}.csv')

# Create a SQLAlchemy engine
engine = create_engine(connection_string)

# Upload the DataFrame to the PostgreSQL database
table_name = 'reports'

merged_data.to_sql(table_name, engine, if_exists='replace', index=False)
