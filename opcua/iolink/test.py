from iodd import IODD
from information_node import InformationNode


with open('ifm-000404-20200110-IODD1.1.xml', 'r') as f:
    data = f.read()

#print(data)

# iodd_test.xml = data
# iodd_test.family ='VVB001'
# iodd_test.total_bit_length =16
# iodd_test.information_nodes ="V_PdT"
info_node = InformationNode("eafo",144,16,1)
""" 
    name : str
        Name of the information point
    bit_offset : int
        offset from the right side of the bit-wise sensor output for a specific
        information point in bits
    bit_length : int
        length of the bit-wise sensor output for a specific information point in bits
    subindex : int
        used for indexing inside the IODD """

iodd_test = IODD(data,['VVB001'],[info_node],20)


iodd_test._parse_information_nodes()
byte_string_1 = [0, 0, 252, 0, 0, 1, 255, 0, 0, 0, 255, 0, 1, 125, 255, 0, 0, 37, 255, 0]
byte_string_2 = [0, 1, 252, 0, 0, 15, 255, 0, 0, 1, 255, 0, 1, 126, 255, 0, 0, 134, 255, 0]
byte_string_3 = [0, 4, 252, 0, 0, 31, 255, 0, 0, 3, 255, 0, 1, 125, 255, 0, 0, 119, 255, 0]
byte_string_4 = [0, 9, 252, 0, 0, 73, 255, 0, 0, 7, 255, 0, 1, 126, 255, 0, 0, 101, 255, 0]
byte_string_5 = [0, 11, 252, 0, 0, 127, 255, 0, 0, 10, 255, 0, 1, 126, 255, 0, 0, 124, 255, 3]
byte_string_6 = [0, 1, 252, 0, 0, 1, 255, 0, 0, 0, 255, 0, 1, 125, 255, 0, 0, 35, 255, 1]
byte_strings = [byte_string_1,byte_string_2,byte_string_3,byte_string_4,byte_string_5,byte_string_6]
for i in byte_strings:

    a = info_node.byte_to_real_value(i)
    print("result ", a)
    print("- units: ['m/s', 'mm/s', 'in/s', 'm/s', 'mm/s', 'in/s']")