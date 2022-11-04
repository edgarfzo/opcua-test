
FX the distance sensor we have in the office:
data that we get looks like : [ 212, 0, 45, 7, 9, 0, 10 , 200]
stream of BYTES 
bit is 0 or 1
byte is 8 bits so its number like 01010101 which is between 0 and 256

We need to translate from bytes to actual data like : Voltage: 5.43 volts
We do this using the IODD.xml file with SPQL (sascha code). 

inputs needed : opcua data stream and iodd file of specific sensor
SPQL CODE implements
0 - Finding the opc-ua nodes (necessary) process data input  it depends only on the iolink master used : we have coretigo (SPQL coded this one) and pebber fuchts.
0.1- In the node you can fetch the name of the sensor -- answer: vvb001 FX
1- Fetching the IODD file from internet (nice feature but no necessary, can be manually imported in the gg component)
2- transfrom the IODD file into a dictionary in python (necessary)
3- appplying that dictionary for translating the data

The lambda reads the bytes stream and translates to data... then to mqtt 

Suniraj and Bheema could make in CDK a nice ending database (timestream or S3) and a nice mqtt topic name convention and nice injestion logic.

So the inputs for Suniraj and Bheema will be: max 8 sensors and 1-3 values per sensor: 0-20 data values each round ---> injest them in a nice way

Final goal:

Client connects sensors and the data is inmediatellly streaming into the databases and nicely stored to be queried afterwards

Tech question: do we need a middlelayer : Lambda scheduler. Case:  if we push data too quiickly to the injestion part. does it scalate??

so data read 5 per second --> data write 1 per second: what happens here??