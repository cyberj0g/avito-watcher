import pandas as pd
import sqlitedict
import config


def load_data():
    db = sqlitedict.SqliteDict(config.DB_PATH, autocommit=True)
    df = pd.DataFrame.from_records(index = list(db.iterkeys()), data=list(db.itervalues()))
    df = df[df['start_url'].isin(config.AVITO_URLS.split(';'))]
    return df
