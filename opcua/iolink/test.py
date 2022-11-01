from iodd import IODD
from information_node import InformationNode


with open('ifm-000404-20200110-IODD1.1.xml', 'r') as f:
    data = f.read()

#print(data)

# iodd_test.xml = data
# iodd_test.family ='VVB001'
# iodd_test.total_bit_length =16
# iodd_test.information_nodes ="V_PdT"
info_node = InformationNode("V_PdT",16,16,6)
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

iodd_test = IODD(data,['VVB001'],[info_node],16)


iodd_test._iodd_to_value_index()