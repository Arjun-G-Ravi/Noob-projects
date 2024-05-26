import pandas as pd


def add_row(db, new_data):
    new_row = pd.DataFrame(new_data, index=[0])
    updated_db = pd.concat([db, new_row], ignore_index=True)
    return updated_db