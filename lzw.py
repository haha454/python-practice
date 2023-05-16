from struct import pack
from struct import unpack
import unittest

CODE_WORD_NUM_BIT = 12
MAXIMUM_DICTIONARY_SIZE = 1 << CODE_WORD_NUM_BIT


def compress(data: str) -> bytes:
    # Building and initializing the dictionary.
    code = 128
    dictionary = {chr(i): i for i in range(code)}
    code += 1

    # We'll start off our phrase as empty and add characters to it as we encounter them
    phrase = ""

    result: bytearray = bytearray()

    def __handle_compressed_data(data: int):
        nonlocal result
        result += pack('>B', data)

    # Iterating through the input text character by character
    for cur in data:
        phrase += cur

        # If we have a match, we'll skip over it
        # This is how we build up to support larger phrases
        if phrase not in dictionary:
            # We'll add the existing phrase (without the breaking character) to our output
            __handle_compressed_data(dictionary[phrase[:-1]])

            # We'll create a new code (if space permits)
            if len(dictionary) < MAXIMUM_DICTIONARY_SIZE:
                dictionary[phrase] = code
                code += 1
            phrase = cur

    assert (phrase in dictionary)
    __handle_compressed_data(dictionary[phrase])

    return result.hex()

def decompress(data: bytes) -> str:
    # Building and initializing the dictionary.
    code = 128
    dictionary = {i: chr(i) for i in range(code)}
    code += 1

    phrase = ""
    result: list[str] = []
    def __handle_decompressed_data(st: str):
        result.append(st)

    for cur in data:
        if cur not in dictionary:
            dictionary[cur] = phrase + phrase[0]
        
        __handle_decompressed_data(dictionary[cur])
        
        if phrase and len(dictionary) <= MAXIMUM_DICTIONARY_SIZE:
            dictionary[code] = phrase + dictionary[cur][0]
            code += 1
        phrase = dictionary[cur]

    return ' '.join(result)


class LzwTest(unittest.TestCase):
    def test_compress(self):
        self.assertEqual('41428183', compress('ABABABA'))

    def test_decompress(self):
        self.assertEqual('A B AB ABA', decompress(b'AB\x81\x83'))

if __name__ == '__main__':
    unittest.main()