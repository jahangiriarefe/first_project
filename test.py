first_name = 'ali'
last_name = 'akbari'

message = 'Hello {} {}'
print(message.format(first_name, last_name))

message = 'Hello {0} {1}'
print(message.format(first_name, last_name))

message = 'Hello {fname} {lname}'
print(message.format(fname=first_name, lname=last_name))