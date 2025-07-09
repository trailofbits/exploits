import pytest
from ..injection.serialization import SimpleProtoBufSerial 
from ..injection.deserialization import SimpleProtoBufDeserial 

def test_zigzag_encoding():
    test_cases = {
        0: 0,
        -1: 1,
        1: 2,
        -2: 3,
        2: 4,
        -2147483648: 4294967295,  # Edge case: Min 32-bit signed int
        2147483647: 4294967294,   # Edge case: Max 32-bit signed int
    }
    for original, encoded in test_cases.items():
        assert SimpleProtoBufSerial._zigzag_encode(original) == encoded

def test_zigzag_decoding():
    test_cases = {
        0: 0,
        1: -1,
        2: 1,
        3: -2,
        4: 2,
        4294967295: -2147483648,  # Edge case: Min 32-bit signed int
        4294967294: 2147483647,   # Edge case: Max 32-bit signed int
    }
    for encoded, original in test_cases.items():
        assert SimpleProtoBufDeserial._zigzag_decode(encoded) == original

def test_serialize_int():
    test_cases = [0, 1, 127, 128, 255, 256, 1024, 65535, 2147483647]
    for num in test_cases:
        # Directly call serialize_int which already includes the type byte
        serialized = SimpleProtoBufSerial._serialize_int(num)
        # Remove the type byte before deserialization
        serialized_without_type = serialized[1:] 
        deserialized, remainder = SimpleProtoBufDeserial._deserialize_int(serialized_without_type)
        assert deserialized == num
        assert remainder == b''  # remainder should be empty after deserialization

def test_serialize_int_general():
    test_cases = [0, 1, 127, 128, 255, 256, 1024, 65535, 2147483647]
    for num in test_cases:
        # Use the general serialize method which includes the type byte
        serialized = SimpleProtoBufSerial.serialize(num)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert deserialized == num

def test_serialize_int_negative():
    test_cases = [0, -1, -127, -128, -255, -256, -1024, -65535, -2147483647]
    for num in test_cases:
        # Directly call serialize_int which already includes the type byte
        serialized = SimpleProtoBufSerial._serialize_int(num)
        # Remove the type byte before deserialization
        serialized_without_type = serialized[1:] 
        deserialized, remainder = SimpleProtoBufDeserial._deserialize_int(serialized_without_type)
        assert deserialized == num
        assert remainder == b''  # remainder should be empty after deserialization

def test_serialize_int_negative_general():
    test_cases = [0, -1, -127, -128, -255, -256, -1024, -65535, -2147483647]
    for num in test_cases:
        # Use the general serialize method which includes the type byte
        serialized = SimpleProtoBufSerial.serialize(num)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert deserialized == num

def test_serialized_length_of_ints():
    """ This test will serialize different integers and assert that smaller integers produce a shorter byte sequence compared to larger integers.
    """
    # Integers that should be serialized into a small length
    smaller_ints = [0, 1, 63]  # These should have shorter serialized lengths

    # Integers that cross the threshold and require more space
    larger_ints = [64, 128, 1024, 65535, 2147483647]  # These should have longer serialized lengths

    for small_int in smaller_ints:
        serialized_small = SimpleProtoBufSerial._serialize_int(small_int)
        small_length = len(serialized_small)

        for large_int in larger_ints:
            serialized_large = SimpleProtoBufSerial._serialize_int(large_int)
            large_length = len(serialized_large)

            # Assert that the length of the serialized smaller int is less than or equal to that of the larger int
            assert small_length <= large_length, f"Serialized length of {small_int} ({small_length}) should be smaller or equal to that of {large_int} ({large_length})"

def test_serialized_length_of_ints_2():
    """This test will serialize different integers and assert that smaller integers produce a shorter byte sequence compared to larger integers.
    """
    # Comparing positive numbers around the threshold
    smaller_positive = 63
    larger_positive = 64
    serialized_smaller_positive = SimpleProtoBufSerial._serialize_int(smaller_positive)
    serialized_larger_positive = SimpleProtoBufSerial._serialize_int(larger_positive)
    assert len(serialized_smaller_positive) < len(serialized_larger_positive), \
        f"Serialized length of {smaller_positive} should be smaller than that of {larger_positive}"

    # Comparing negative numbers around the threshold
    smaller_negative = -64
    larger_negative = -65
    serialized_smaller_negative = SimpleProtoBufSerial._serialize_int(smaller_negative)
    serialized_larger_negative = SimpleProtoBufSerial._serialize_int(larger_negative)
    assert len(serialized_smaller_negative) < len(serialized_larger_negative), \
        f"Serialized length of {smaller_negative} should be smaller than that of {larger_negative}"

def test_serialize_float():
    test_cases = [0.0, 1.0, -1.0, 123.456, -123.456, 1.234e5]
    for num in test_cases:
        # Call serialize_float which includes the type byte
        serialized = SimpleProtoBufSerial._serialize_float(num)
        # Remove the type byte before deserialization
        serialized_without_type = serialized[1:]
        deserialized, remainder = SimpleProtoBufDeserial._deserialize_float(serialized_without_type)
        assert pytest.approx(deserialized) == num
        assert remainder == b''  # Check that remainder is empty after deserialization

def test_serialize_float_general():
    test_cases = [0.0, 1.0, -1.0, 123.456, -123.456, 1.234e5]
    for num in test_cases:
        # Use the general serialize method
        serialized = SimpleProtoBufSerial.serialize(num)
        # Deserialize and don't worry about the type byte, as it's handled internally
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert pytest.approx(deserialized) == num

def test_serialize_list_int():
    test_cases = [[], [1, 2, 3], [100, 200, 300], [2147483647, 0]]
    for lst in test_cases:
        serialized = SimpleProtoBufSerial._serialize_list(lst)
        deserialized, remainder = SimpleProtoBufDeserial._deserialize_list(serialized[1:])  # Remove type byte
        assert deserialized == lst
        assert remainder == b''  # remainder should be empty

def test_serialize_list_int_general():
    test_cases = [[], [1, 2, 3], [100, 200, 300], [2147483647, 0]]
    for lst in test_cases:
        serialized = SimpleProtoBufSerial.serialize(lst)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert deserialized == lst

def test_serialize_list_float():
    test_cases = [[], [1.0, 2.0, 3.0], [100.5, 200.5, 300.5], [-1.234, 0.456, 789.1]]
    for lst in test_cases:
        serialized = SimpleProtoBufSerial._serialize_list(lst)
        deserialized, remainder = SimpleProtoBufDeserial._deserialize_list(serialized[1:])  # Remove type byte
        assert all(a == pytest.approx(b) for a, b in zip(deserialized, lst))
        assert remainder == b''  # remainder should be empty

def test_serialize_list_float_general():
    test_cases = [[], [1.0, 2.0, 3.0], [100.5, 200.5, 300.5], [-1.234, 0.456, 789.1]]
    for lst in test_cases:
        serialized = SimpleProtoBufSerial.serialize(lst)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert all(a == pytest.approx(b) for a, b in zip(deserialized, lst))

def test_serialize_list_list_int():
    test_cases = [[], [[1, 2], [3, 4]], [[100], [200, 300]], [[2147483647], [0, -1]]]
    for lst in test_cases:
        serialized = SimpleProtoBufSerial._serialize_list(lst)
        deserialized, remainder = SimpleProtoBufDeserial._deserialize_list(serialized[1:])  # Remove type byte
        assert deserialized == lst
        assert remainder == b''  # remainder should be empty

def test_serialize_list_list_int_general():
    test_cases = [[], [[1, 2], [3, 4]], [[100], [200, 300]], [[2147483647], [0, -1]]]
    for lst in test_cases:
        serialized = SimpleProtoBufSerial.serialize(lst)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert deserialized == lst

def test_serialize_list_tuple_int_general():
    test_cases = [(), [(1, 2), (3, 4)], [(100,), (200, 300)], [(2147483647,), (0, -1)]]
    for tpl in test_cases:
        serialized = SimpleProtoBufSerial.serialize(tpl)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert deserialized == tpl

def test_serialize_list_dict_int_general():
    test_cases = [{}, [{1: 10, 2: 20}, {3: 30, 4: 40}], [{100: 1000}, {200: 2000, 300: 3000}], [{2147483647: 2147483647}, {0: 0, -1: -1}]]
    for dct in test_cases:
        serialized = SimpleProtoBufSerial.serialize(dct)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert deserialized == dct

def test_serialize_tuple_int():
    test_cases = [(), (1, 2, 3), (100, 200, 300), (2147483647, 0)]
    for tpl in test_cases:
        serialized = SimpleProtoBufSerial._serialize_tuple(tpl)
        # Remove type byte before deserialization
        deserialized, remainder = SimpleProtoBufDeserial._deserialize_tuple(serialized[1:])
        assert deserialized == tpl
        assert remainder == b''  # Check that remainder is empty

def test_serialize_tuple_int_general():
    test_cases = [(), (1, 2, 3), (100, 200, 300), (2147483647, 0)]
    for tpl in test_cases:
        serialized = SimpleProtoBufSerial.serialize(tpl)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert deserialized == tpl

def test_serialize_tuple_float_general():
    test_cases = [(), (1.0, 2.0, 3.0), (100.5, 200.5, 300.5), (-1.234, 0.456, 789.1)]
    for tpl in test_cases:
        serialized = SimpleProtoBufSerial.serialize(tpl)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert all(a == pytest.approx(b) for a, b in zip(deserialized, tpl))

def test_serialize_tuple_tuple_int_general():
    test_cases = [(), ((1, 2), (3, 4)), ((100,), (200, 300)), ((2147483647,), (0, -1))]
    for tpl in test_cases:
        serialized = SimpleProtoBufSerial.serialize(tpl)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert deserialized == tpl

def test_serialize_tuple_list_int_general():
    test_cases = ((), ([1, 2, 3], [4, 5, 6]), ([100, 101], [200, 201, 202]), ([2147483647], [0, -1, -2]))
    for lst in test_cases:
        serialized = SimpleProtoBufSerial.serialize(lst)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert deserialized == lst

def test_serialize_tuple_dict_int_general():
    test_cases = ((), ({1: 10, 2: 20}, {3: 30, 4: 40}), ({100: 1000}, {200: 2000, 300: 3000}), ({2147483647: 2147483647}, {0: 0, -1: -1}))
    for dct in test_cases:
        serialized = SimpleProtoBufSerial.serialize(dct)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert deserialized == dct

def test_serialize_dict_int():
    test_cases = [
        {},
        {1: 10, 2: 20, 3: 30},
        {100: 1000, 200: 2000},
        {2147483647: 0, 123456: 7890}
    ]
    for dct in test_cases:
        serialized = SimpleProtoBufSerial._serialize_dict(dct)
        # Remove type byte before deserialization
        deserialized, remainder = SimpleProtoBufDeserial._deserialize_dict(serialized[1:])
        assert deserialized == dct
        assert remainder == b''  # Check that remainder is empty

def test_serialize_dict_int_general():
    test_cases = [
        {},
        {1: 10, 2: 20, 3: 30},
        {100: 1000, 200: 2000},
        {2147483647: 0, 123456: 7890}
    ]
    for dct in test_cases:
        serialized = SimpleProtoBufSerial.serialize(dct)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert deserialized == dct

def test_serialize_dict_float_general():
    test_cases = [
        {},
        {1: 1.0, 2: 2.0, 3: 3.0},
        {100: 100.5, 200: 200.5},
        {2147483647: -0.123, 123456: 789.1}
    ]
    for dct in test_cases:
        serialized = SimpleProtoBufSerial.serialize(dct)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert all(deserialized[k] == pytest.approx(v) for k, v in dct.items())

def test_serialize_dict_dict_int_general():
    test_cases = [
        {},
        {1: {10: 100, 20: 200}, 2: {30: 300}},
        {100: {1000: 10000}, 200: {2000: 20000}},
        {2147483647: {0: -1}, 123456: {7890: 1234}}
    ]
    for dct in test_cases:
        serialized = SimpleProtoBufSerial.serialize(dct)
        deserialized, _ = SimpleProtoBufDeserial.deserialize(serialized)
        assert deserialized == dct

def test_serialize_stream_multiple_ints():
    """In this test:
    We first serialize each integer from the test cases and concatenate them into a single bytearray, creating a continuous byte stream.
    Then, we deserialize each integer from this stream in sequence. Since each call to deserialize returns the deserialized value and the remainder of the byte stream, we can continue to deserialize the next integer from the remaining stream.
    After all integers are deserialized, we assert that the remaining byte stream is empty, ensuring that there are no leftover bytes and that all integers have been properly deserialized.
    """
    test_cases = [0, 1, 127, 128, 255, 256, 1024, 65535, 2147483647]
    # Serialize multiple integers into a single byte stream
    serialized_stream = bytearray()
    for num in test_cases:
        serialized_stream += SimpleProtoBufSerial.serialize(num)
    
    # Deserialize each integer in sequence from the byte stream
    for num in test_cases:
        deserialized, serialized_stream = SimpleProtoBufDeserial.deserialize(serialized_stream)
        assert deserialized == num
        # The remaining stream is passed back for the next deserialization

    # After all deserializations, the stream should be empty
    assert serialized_stream == b''

def test_serialize_stream_mixed_int_float_list_tuple_dict():
    """
    This test serializes a sequence of mixed data types into a single byte stream and then deserializes each item.
    It checks that all items are properly deserialized with special handling for floats using pytest.approx.
    """
    test_cases = [
        42,                                   # Integer
        3.14,                                 # Float
        [1, 2, 3],                            # List of Integers
        (4.5, 6.7),                           # Tuple of Floats
        {1: [1.1, 2.2], 2: [3.3, 4.4]},       # Dictionary with Lists of Floats
        [(10, 20), (30, 40)],                 # List of Tuples (Integers)
        {100: (1.1, 2.2), 200: (3.3, 4.4)}    # Dictionary with Tuples of Floats
    ]

    # Serialize the mixed data types into a single byte stream
    serialized_stream = bytearray()
    for item in test_cases:
        serialized_stream += SimpleProtoBufSerial.serialize(item)

    # Deserialize each item in sequence from the byte stream
    for expected_item in test_cases:
        deserialized_item, serialized_stream = SimpleProtoBufDeserial.deserialize(serialized_stream)
        
        if isinstance(deserialized_item, float):
            assert pytest.approx(deserialized_item) == expected_item
        elif isinstance(deserialized_item, tuple) and all(isinstance(x, float) for x in deserialized_item):
            for deserialized_element, expected_element in zip(deserialized_item, expected_item):
                assert pytest.approx(deserialized_element) == expected_element
        elif isinstance(deserialized_item, dict):
            for key in deserialized_item:
                if isinstance(deserialized_item[key], float):
                    assert pytest.approx(deserialized_item[key]) == expected_item[key]
                elif isinstance(deserialized_item[key], tuple):
                    for deserialized_element, expected_element in zip(deserialized_item[key], expected_item[key]):
                        assert pytest.approx(deserialized_element) == expected_element
        else:
            assert deserialized_item == expected_item

    # After all deserializations, the stream should be empty
    assert serialized_stream == b''

def test_serialize_dict_int_list_list_tuple_int_int_float_general():
    """
    This is an example of one of the structures we are using in our proof of concept.
    This test serializes and deserializes dictionaries with complex nested structures.
    It includes integers, lists, tuples, and floats, with special handling for floating-point precision.
    """
    test_cases = [
        {},
        {2: [[((3, 2), 18.945833),
              ((11, 2), 9.899415),
              ((18, 2), 8.650933),
              ((39, 2), 3.2750032),
              ((44, 2), 3.7911563),
              ((55, 2), 3.1947412)],
             []]},
        {100: [[((10, 5), 15.123),
                ((20, 5), 25.456)]],
         200: [[((30, 10), 35.789)]]
        },
        {2147483647: [[((40, 20), 45.012),
                       ((50, 25), 55.034)]],
         123456: [[((60, 30), 65.056),
                   ((70, 35), 75.078)]]
        },
        {0: [],
        1: [[((667, 3), 0.097110935),
            ((667, 11), 0.6439785),
            ((667, 18), 0.8416387),
            ((667, 39), 0.18489307),
            ((667, 44), 0.085414834),
            ((667, 55), 0.06560838),
            ((668, 3), 0.05347056),
            ((668, 11), 0.52310777),
            ((668, 18), 0.98487437),
            ((668, 39), 0.33244213),
            ((668, 44), 0.31549022),
            ((668, 55), 0.031622093),
            ((669, 3), 0.090587094),
            ((669, 11), 0.24350557),
            ((669, 18), 0.43878964),
            ((669, 39), 0.2731838),
            ((669, 44), 0.27340847),
            ((669, 55), 0.109154135),
            ((670, 3), 0.11667683),
            ((670, 11), 0.2779597),
            ((670, 18), 0.35213044),
            ((670, 39), 0.025092779),
            ((670, 44), 0.020467341),
            ((670, 55), 0.064510435),
            ((695, 3), 0.06806233),
            ((695, 11), 0.52899784),
            ((695, 18), 0.96612585),
            ((695, 39), 0.11631002),
            ((695, 44), 0.0810911),
            ((695, 55), 0.102051556),
            ((696, 3), 0.16189218),
            ((696, 11), 0.21963857),
            ((696, 18), 0.16213672),
            ((696, 39), 0.10578254),
            ((696, 44), 0.21028459),
            ((696, 55), 0.2457161),
            ((697, 3), 0.110124156),
            ((697, 11), 0.62209594),
            ((697, 18), 0.6951123),
            ((697, 39), 0.0061920094),
            ((697, 44), 0.26062098),
            ((697, 55), 0.30955908),
            ((698, 3), 0.1330668),
            ((698, 11), 0.06536835),
            ((698, 18), 0.40478894),
            ((698, 39), 0.19496274),
            ((698, 44), 0.15035558),
            ((698, 55), 0.251647),
            ((723, 3), 0.034877624),
            ((723, 11), 0.1506983),
            ((723, 18), 1.2693334),
            ((723, 39), 0.1052212),
            ((723, 44), 0.16704611),
            ((723, 55), 0.29637942),
            ((724, 3), 0.1083501),
            ((724, 11), 0.57521397),
            ((724, 18), 0.57365555),
            ((724, 39), 0.19592753),
            ((724, 44), 0.15228069),
            ((724, 55), 0.0062229126),
            ((725, 3), 0.08201416),
            ((725, 11), 0.5766261),
            ((725, 18), 0.35527176),
            ((725, 39), 0.33244404),
            ((725, 44), 0.3319978),
            ((725, 55), 0.0014897585),
            ((726, 3), 0.048295148),
            ((726, 11), 0.65974873),
            ((726, 18), 0.8377941),
            ((726, 39), 0.2955989),
            ((726, 44), 0.105835326),
            ((726, 55), 0.046030432),
            ((751, 3), 0.011523995),
            ((751, 11), 0.66270506),
            ((751, 18), 1.1027086),
            ((751, 39), 0.2960945),
            ((751, 44), 0.22085945),
            ((751, 55), 0.020261493),
            ((752, 3), 0.13854772),
            ((752, 11), 0.20427918),
            ((752, 18), 0.023307392),
            ((752, 39), 0.23623456),
            ((752, 44), 0.054653212),
            ((752, 55), 0.14988005),
            ((753, 3), 0.13332362),
            ((753, 11), 0.4646727),
            ((753, 18), 0.62406385),
            ((753, 39), 0.20937763),
            ((753, 44), 0.27695876),
            ((753, 55), 0.13539663),
            ((754, 3), 0.14972317),
            ((754, 11), 0.07092172),
            ((754, 18), 1.2653555),
            ((754, 39), 0.07786918),
            ((754, 44), 0.032505333),
            ((754, 55), 0.27682546)],
            [((3,), -0.33320472),
            ((11,), -4.2749963),
            ((18,), -6.7155576),
            ((39,), -1.2354791),
            ((44,), -1.4925873),
            ((55,), -0.09620837)]],
        2: [[((3, 2), 18.945833),
            ((11, 2), 9.899415),
            ((18, 2), 8.650933),
            ((39, 2), 3.2750032),
            ((44, 2), 3.7911563),
            ((55, 2), 3.1947412)],
            []]
        }
    ]
    for original_dct in test_cases:
        serialized = SimpleProtoBufSerial.serialize(original_dct)
        deserialized_dct, _ = SimpleProtoBufDeserial.deserialize(serialized)
    
        for key, deserialized_value in deserialized_dct.items():
            for sublist_index, deserialized_sublist in enumerate(deserialized_value):
                for tuple_index, deserialized_tuple in enumerate(deserialized_sublist):
                    # Extracting the corresponding tuple from the original data
                    original_tuple = original_dct[key][sublist_index][tuple_index]

                    # Comparing the integer part of the tuple
                    assert deserialized_tuple[0] == original_tuple[0]

                    # Comparing the float part of the tuple using pytest.approx for precision handling
                    assert pytest.approx(deserialized_tuple[1]) == original_tuple[1]
