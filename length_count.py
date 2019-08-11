import os
import pandas as pd


def length_count(csv_file, path):
    """
    Function counts average articles length for all articles in a folder {path}
    The name of csv file with meta information is required{csv_file}
    The function returns a dictionary with sources as key values
    and average lengths as values
    """

    data = pd.read_csv(csv_file)

    d = {item: [] for item in data['источник'].unique()}
    os.chdir(path)

    for filename in os.listdir(os.getcwd()):
        if filename.endswith('_s.txt'):
            source = data[data['Статья'] == filename]['источник']
            source = source.to_string(index=False).strip(' ')
            with open(filename, 'r') as f:
                try:
                    d[source].append(len(f.read()))
                except:
                    pass

    # for key in d.keys():
        # print(key, '- ', len(d[key]))

    final_d = {key: round(sum([int(x) for x in d[key]]) / len(d[key]), 2)
               for key in d.keys() if len(d[key]) != 0}
    return final_d


if __name__ == "__main__":
    result = length_count('Practice.csv', os.getcwd()+r'\praktika')
    print(result)
