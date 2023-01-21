def remove_outliers(df, columns, n_std):
    for col in columns:
        print('Removing outlieres from column: {}'.format(col))

        mean = df[col].mean()
        sd = df[col].std()

        df = df[(df[col] <= mean + (n_std * sd))]

    return df
