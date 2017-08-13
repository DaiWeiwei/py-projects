class ByteArrayStringOperaion(object):
    @staticmethod
    def fill_zero(byte_array_string, max_len, from_left):
        if not byte_array_string:
            return byte_array_string
        if from_left:
            string_format = '{:0>' + str(max_len) + '}'
        else:
            string_format = '{:0<' + str(max_len) + '}'
        if type(byte_array_string) is list:
            return ByteArrayStringOperaion._fill_zero_for_list(byte_array_string, string_format)
        else:
            return string_format.format(byte_array_string)

    @staticmethod
    def _fill_zero_for_list(byte_array_string_list, string_format):
        for index, byte_array_string in enumerate(byte_array_string_list):
            if byte_array_string is None:
                continue
            byte_array_string_list[index] = string_format.format(byte_array_string)
        return byte_array_string_list

    @staticmethod
    def fill_zero_from_left(byte_array_string, max_len):
        return ByteArrayStringOperaion.fill_zero(byte_array_string, max_len, True)

    @staticmethod
    def fill_zero_from_right(byte_array_string, max_len):
        return ByteArrayStringOperaion.fill_zero(byte_array_string, max_len, False)

    @staticmethod
    def convert_string_to_byte_array_string(string_buffer):
        if string_buffer is None:
            return None
        if not isinstance(string_buffer, basestring):
            raise Exception('{0} is not string type!'.format(type(string_buffer)))
        result = []
        for c in string_buffer:
            result.append(hex(ord(c)).lstrip('0x'))
        string_buffer = ''.join(result)
        return string_buffer


if __name__ == '__main__':
    pass