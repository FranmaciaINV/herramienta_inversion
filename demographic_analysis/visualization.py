import matplotlib.pyplot as plt

def plot_population_pyramid(df, age_column, gender_column):
    """
    Genera una pirámide poblacional a partir de datos de edad y género.
    """
    male_data = df[df[gender_column] == 'M']
    female_data = df[df[gender_column] == 'F']

    plt.figure(figsize=(10, 7))
    plt.barh(male_data[age_column], male_data["count"], color='blue', label='Hombres')
    plt.barh(female_data[age_column], -female_data["count"], color='pink', label='Mujeres')
    plt.legend()
    plt.title("Pirámide poblacional")
    plt.show()
