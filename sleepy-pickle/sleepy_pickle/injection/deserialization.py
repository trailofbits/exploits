# Note: This file's contents are used literally as injection source
import struct # This is also used by pickle, therefore its importation isn't suspicious. See pickle_uses_struct.py for proof.

class SimpleProtoBufDeserial:
    """ This is a simplified Protobuf implementation for Python data types restricted to int, float, list, tuple, and dict, 
    with objects being arbitrary compositions of these data types only.

    Usage:
    Call SimpleProtoBufDeserial.deserialize(x_bytearray) to deserialize it.
    """
    # Define magic bytes for each type
    TYPE_INT = 0x01
    TYPE_FLOAT = 0x02
    TYPE_LIST = 0x03
    TYPE_TUPLE = 0x04
    TYPE_DICT = 0x05

    @staticmethod
    def deserialize(serialized):
        """ Returns the Python object from the bytearray `serialized`.
        Also returns the remainder of your bytearray, which will be empty if called from the top-level.
        """
        if not serialized:
            return None, bytearray()

        type_byte = serialized[0]
        if type_byte == SimpleProtoBufDeserial.TYPE_INT:
            return SimpleProtoBufDeserial._deserialize_int(serialized[1:])
        elif type_byte == SimpleProtoBufDeserial.TYPE_FLOAT:
            return SimpleProtoBufDeserial._deserialize_float(serialized[1:])
        elif type_byte == SimpleProtoBufDeserial.TYPE_LIST:
            return SimpleProtoBufDeserial._deserialize_list(serialized[1:])
        elif type_byte == SimpleProtoBufDeserial.TYPE_TUPLE:
            return SimpleProtoBufDeserial._deserialize_tuple(serialized[1:])
        elif type_byte == SimpleProtoBufDeserial.TYPE_DICT:
            return SimpleProtoBufDeserial._deserialize_dict(serialized[1:])
        else:
            raise TypeError(f"Unknown type byte: {type_byte}")

    # Traditionally used in Protobufs for accomodating negative integers
    @staticmethod
    def _zigzag_decode(value):
        return (value >> 1) ^ -(value & 1)

    @staticmethod
    def _deserialize_int(serialized):
        result, remainder = 0, serialized
        shift = 0
        for i, byte in enumerate(serialized):
            result |= (byte & 0x7F) << shift
            shift += 7
            if not (byte & 0x80):
                remainder = serialized[i + 1:]
                break
        return SimpleProtoBufDeserial._zigzag_decode(result), remainder

    @staticmethod
    def _deserialize_float(serialized):
        value, = struct.unpack('f', serialized[:4])
        return value, serialized[4:]
    
    @staticmethod
    def _deserialize_object_length(serialized):
        """ Returns `length` is an int, `remainder` is a bytearray
        """
        length, remainder = SimpleProtoBufDeserial._deserialize_int(serialized[1:]) # skip the type byte
        return length, remainder

    @staticmethod
    def _deserialize_list(serialized):
        length, remainder = SimpleProtoBufDeserial._deserialize_object_length(serialized)
        lst = []
        for _ in range(length):
            item, remainder = SimpleProtoBufDeserial.deserialize(remainder)
            lst.append(item)
        return lst, remainder
    
    @staticmethod
    def _deserialize_tuple(serialized):
        length, remainder = SimpleProtoBufDeserial._deserialize_object_length(serialized)
        tpl = []
        for _ in range(length):
            item, remainder = SimpleProtoBufDeserial.deserialize(remainder)
            tpl.append(item)
        return tuple(tpl), remainder
    
    @staticmethod
    def _deserialize_dict(serialized):
        length, remainder = SimpleProtoBufDeserial._deserialize_object_length(serialized)
        dct = {}
        for _ in range(length):
            key, remainder = SimpleProtoBufDeserial.deserialize(remainder)
            value, remainder = SimpleProtoBufDeserial.deserialize(remainder)
            dct[key] = value
        return dct, remainder
