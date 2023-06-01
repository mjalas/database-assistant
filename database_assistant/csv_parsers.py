import csv


def parse_csv(filepath: str):
    data = []

    with open(filepath, "r") as csv_file:
        reader = csv.reader(csv_file)
        header = None
        for row in reader:
            if header is None:
                header = row
                continue

            data_row = {}
            for count, value in enumerate(row):
                if isinstance(value, str) and value.startswith("{"):
                    # data_row[header[count]] = json.loads(value)
                    data_row[header[count]] = value  # using as str for now
                else:
                    data_row[header[count]] = value

            data.append(data_row)

    return data
