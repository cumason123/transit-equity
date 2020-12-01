from rtc_transit_equity.datasets import generate

if __name__ == '__main__':
    datasets = generate()
    print(datasets.keys())