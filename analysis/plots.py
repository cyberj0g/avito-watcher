import pandas
from matplotlib import pyplot as plt

pandas.set_option('display.width', 200)
pandas.set_option('display.max_columns', 20)
plt.style.use('ggplot')


def plot_prices(data):
    plt.hist(data['price'], bins='auto')
    plt.title('Price histogram')
    plt.show()
