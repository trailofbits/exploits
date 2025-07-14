import struct # This is also used by pickle, therefore its importation isn't suspicious. See pickle_uses_struct.py for proof.
from .deserialization import SimpleProtoBufDeserial

class SimpleProtoBufSerial:
    """ This is a simplified Protobuf implementation for Python data types restricted to int, float, list, tuple, and dict, 
    with objects being arbitrary compositions of these data types only.

    Usage:
    Call SimpleProtoBufSerial.serialize(x) on your object x to serialize it into a bytearray.
    """
    # Define magic bytes for each type
    # Ensure consistency between the two classes
    TYPE_INT = SimpleProtoBufDeserial.TYPE_INT
    TYPE_FLOAT = SimpleProtoBufDeserial.TYPE_FLOAT
    TYPE_LIST = SimpleProtoBufDeserial.TYPE_LIST
    TYPE_TUPLE = SimpleProtoBufDeserial.TYPE_TUPLE
    TYPE_DICT = SimpleProtoBufDeserial.TYPE_DICT

    @staticmethod
    def serialize(value):
        """ Returns the serialized version of `value` as a bytearray
        """
        if isinstance(value, int):
            return SimpleProtoBufSerial._serialize_int(value)
        elif isinstance(value, float):
            return SimpleProtoBufSerial._serialize_float(value)
        elif isinstance(value, list):
            return SimpleProtoBufSerial._serialize_list(value)
        elif isinstance(value, tuple):
            return SimpleProtoBufSerial._serialize_tuple(value)
        elif isinstance(value, dict):
            return SimpleProtoBufSerial._serialize_dict(value)
        else:
            raise TypeError("Unsupported type for serialization")

    # Traditionally used in Protobufs for accomodating negative integers
    @staticmethod
    def _zigzag_encode(value):
        return (value << 1) ^ (value >> 31)

    @staticmethod
    def _serialize_int(value):
        value = SimpleProtoBufSerial._zigzag_encode(value)
        result = bytearray([SimpleProtoBufSerial.TYPE_INT])
        while value > 0x7F:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return result
    
    @staticmethod
    def _serialize_float(value):
        return bytearray([SimpleProtoBufSerial.TYPE_FLOAT]) + struct.pack('f', value)

    @staticmethod
    def _serialize_list(lst):
        serialized = bytearray([SimpleProtoBufSerial.TYPE_LIST])
        serialized += SimpleProtoBufSerial._serialize_int(len(lst))
        for item in lst:
            serialized += SimpleProtoBufSerial.serialize(item)  # Handle arbitrary types
        return serialized
    

    @staticmethod
    def _serialize_tuple(tpl):
        serialized = bytearray([SimpleProtoBufSerial.TYPE_TUPLE])
        serialized += SimpleProtoBufSerial._serialize_int(len(tpl))
        for item in tpl:
            serialized += SimpleProtoBufSerial.serialize(item)
        return serialized
    
    @staticmethod
    def _serialize_dict(dictionary):
        serialized = bytearray([SimpleProtoBufSerial.TYPE_DICT])
        serialized += SimpleProtoBufSerial._serialize_int(len(dictionary))
        for key, value in dictionary.items():
            serialized += SimpleProtoBufSerial.serialize(key)
            serialized += SimpleProtoBufSerial.serialize(value)
        return serialized
    