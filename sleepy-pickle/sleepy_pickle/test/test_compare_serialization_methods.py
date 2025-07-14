import os
import pickle
from ..injection.serialization import SimpleProtoBufSerial
import random
import sys

def generate_mock_data(entry_count, list_length, tuple_count):
    """
    Generates mock data with the structure int -> list of list of tuple (tuple (int, int), float).
    entry_count: Number of entries in the dictionary.
    list_length: Length of each list in the dictionary values.
    tuple_count: Number of tuples in each inner list.
    """
    data = {}
    for _ in range(entry_count):
        key = random.randint(0, 2147483647)
        nested_lists = []
        for _ in range(list_length):
            inner_tuples = [((random.randint(0, 1000), random.randint(0, 100)), random.uniform(0, 100)) for _ in range(tuple_count)]
            nested_lists.append(inner_tuples)
        data[key] = nested_lists
    return data

def write_data_to_file(data, file_name):
    """
    Writes the given data to a text file using its string representation.
    """
    with open(file_name, 'w') as file:
        file.write(repr(data))

def get_file_size(file_name):
    """
    Returns the file size in bytes.
    """
    return sys.getsizeof(open(file_name, 'rb').read())

def main_generate(desired_kilobytes, file_name):
    print("Generating...")
    # Parameters for data generation
    desired_size_bytes = desired_kilobytes * 1024  # KB in bytes
    current_size_bytes = 0
    entry_count = 1
    list_length = 1
    tuple_count = 1

    # Generate data and check size
    while current_size_bytes < desired_size_bytes:
        mock_data = generate_mock_data(entry_count, list_length, tuple_count)
        write_data_to_file(mock_data, file_name)
        current_size_bytes = get_file_size(file_name)
        # Increase the size of the data structure for the next iteration if needed
        if tuple_count < 10:
            tuple_count += 1
        elif list_length < 10:
            list_length += 1
        else:
            entry_count += 1

    print(f"Generated file size: {current_size_bytes / 1024} KB")

def serialize_and_save(file_path, serialization_method, extension):
    with open(file_path, "r") as f:
        content = eval(f.read())

    serialized_file = file_path + extension
    with open(serialized_file, "wb") as s:
        data = serialization_method(content)
        s.write(data)
    return os.path.getsize(serialized_file)

def main_compare(files):
    results = []

    # Find the length of the longest filename
    max_filename_length = max(len(file_path) for file_path in files)

    for file_path in files:
        original_size = os.path.getsize(file_path)

        pickled_size = serialize_and_save(
            file_path,
            lambda x: pickle.dumps(x, protocol=pickle.HIGHEST_PROTOCOL),
            ".pickled.pkl"
        )

        protobuf_size = serialize_and_save(
            file_path,
            SimpleProtoBufSerial.serialize,
            ".simpleprotobuf.txt"
        )

        results.append((file_path, original_size, pickled_size, protobuf_size))

    # Adjust the first column width dynamically based on the longest filename
    filename_column_width = max_filename_length + 2

    header_format = f"{{:<{filename_column_width}}} {{:>15}} {{:>15}} {{:>15}}"
    row_format = f"{{:<{filename_column_width}}} {{:15}} {{:15}} {{:15}}"

    print(header_format.format('File', 'Original Size', 'Pickled Size', 'ProtoBuf Size'))
    for file, original, pickled, protobuf in results:
        print(row_format.format(file, original, pickled, protobuf))

def test_compare_serialization_methods():
    main_generate(desired_kilobytes=200, file_name="/tmp/mock_serial_input_200KB.txt")
    main_generate(desired_kilobytes=1000, file_name="/tmp/mock_serial_input_1MB.txt")
    main_compare(files=["/tmp/mock_serial_input_200KB.txt", "/tmp/mock_serial_input_1MB.txt"])
