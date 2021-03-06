# This driver uses arduino to control both MW switches, 
# needs COM module.
#                                             -- Arpit

# from Arduino import serial_write
from Serial_TCP_client_functions import serial_write



def set_rt_switch(pos):
	if pos=='NC':
		serial_write(6)
	elif pos=='NO':
		serial_write(7)
	else:
		print('### ERROR: Room temperature switch input error.')


def set_cryo_switch(pos):
	if pos==1:
		serial_write(4)
	elif pos==2:
		serial_write(5)
	else:
		print('### ERROR: Cryo switch input error.')