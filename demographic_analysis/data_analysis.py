def calculate_statistics(df, column_name):
    """
    Calcula estadísticas básicas (media, mediana, desviación estándar) para una columna dada.
    """
    stats = {
        "mean": df[column_name].mean(),
        "median": df[column_name].median(),
        "std_dev": df[column_name].std()
    }
    return stats

def calculate_percentage(df, part_column, total_column):
    """
    Calcula el porcentaje de una columna respecto a otra.
    """
    df["percentage"] = (df[part_column] / df[total_column]) * 100
    return df
