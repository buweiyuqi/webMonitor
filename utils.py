import pandas as pd


def convert(col, idx):
    obj = eval(col)
    # res = f'https:{obj[idx]["url"]}'
    return f'https:{obj[idx]["url"]}' if len(obj) > idx else None


def flatten_json(csv_file):
    format = csv_file.rsplit('.')
    if format[-1] == 'xlsx':
        products = pd.read_excel(csv_file)
    else:
        products = pd.read_csv(csv_file)
    for i in range(3):
        products[f'image_url_{i}'] = products['assets'].apply(convert, args=(i,))
    products.to_excel('hermes_products_woman_12_30.xlsx', index=False)


if __name__ == '__main__':
    flatten_json('hermes_products_woman.xlsx')
