# -*- coding: utf-8 -*-
# This is a Qcodes driver for Redpitaya card SCPI IQ server 
# written by Martina Esposito and Arpit Ranadive, 2019/2020
#

from time import sleep
import time 
import numpy as np
#import qt
#import ctypes  # only for DLL-based instrument

import qcodes as qc
from qcodes import (Instrument, VisaInstrument,
                    ManualParameter, MultiParameter,
                    validators as vals)
from qcodes.instrument.channel import InstrumentChannel
import matplotlib.pyplot as plt
from qcodes.instrument.parameter import ParameterWithSetpoints, Parameter
from qcodes.utils.validators import Numbers, Arrays




class GeneratedSetPoints(Parameter):
    """
    A parameter that generates a setpoint array from start, stop and num points
    parameters.
    """
    def __init__(self, startparam, stopparam, numpointsparam, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._startparam = startparam
        self._stopparam = stopparam 
        self._numpointsparam = numpointsparam

    def get_raw(self):
        return np.linspace(self._startparam(), self._stopparam() -1,
                              self._numpointsparam())


class IQ_INT(ParameterWithSetpoints):

    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._channel = channel

    def get_raw(self):
        time.sleep(0.2)
        data = self._instrument.get_data()
        if self._channel == 'I1':
            data_ret = data[0]
        elif self._channel == 'Q1':
            data_ret = data[1]
        elif self._channel == 'I2':
            data_ret = data[2]
        else:
            data_ret = data[3]
        return data_ret


class IQ_INT_all(Parameter):

    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._channel = channel

    def get_raw(self):
        #time.sleep(0.2) ### test
        data = self._instrument.get_data()
        data_ret_I1 = np.array([data[0]])
        data_ret_Q1 = np.array([data[1]])
        data_ret_I2 = np.array([data[2]])
        data_ret_Q2 = np.array([data[3]])
        data_ret = np.concatenate((data_ret_I1,data_ret_Q1,data_ret_I2,data_ret_Q2)).T
        return data_ret


class IQ_INT_AVG(Parameter):

    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._channel = channel

    def get_raw(self):
        time.sleep(0.2)
        data = self._instrument.get_data()
        if self._channel == 'I1':
            data_ret = np.mean(data[0])
        elif self._channel == 'Q1':
            data_ret = np.mean(data[1])
        elif self._channel == 'I2':
            data_ret = np.mean(data[2])
        else:
            data_ret = np.mean(data[3])
        return data_ret



class IQ_INT_AVG_all(Parameter):

    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._channel = channel

    def get_raw(self):
        time.sleep(0.2)
        data = self._instrument.get_data()
        data_ret_I1 = np.mean(data[0])
        data_ret_Q1 = np.mean(data[1])
        data_ret_I2 = np.mean(data[2])
        data_ret_Q2 = np.mean(data[3])
        return [data_ret_I1,data_ret_Q1,data_ret_I2,data_ret_Q2]



class ADC_power(ParameterWithSetpoints):

    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._channel = channel

    def get_raw(self):
        time.sleep(0.2)
        data = self._instrument.get_data()
        # data_ret_I1 = (np.mean(data[0]**2)-np.mean(data[0])**2)/50
        # data_ret_Q1 = (np.mean(data[1]**2)-np.mean(data[1])**2)/50
        # data_ret_I2 = (np.mean(data[2]**2)-np.mean(data[2])**2)/50
        # data_ret_Q2 = (np.mean(data[3]**2)-np.mean(data[3])**2)/50
        A_1 = (np.mean(data[0]**2 + data[1]**2))/50
        A_2 = (np.mean(data[2]**2 + data[3]**2))/50
        #data_ret_I1+data_ret_Q1,data_ret_I2+data_ret_Q2,
        return np.array([ A_1, A_2])



class IQ_CH1(ParameterWithSetpoints):

    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._channel = channel

    def get_raw(self):
        time.sleep(0.2)
        data = self._instrument.get_data()
        if self._channel == 'I1':
            data_ret = data[0]
        elif self._channel == 'Q1':
            data_ret = data[1]
        else:
            print('Wrong parameter.')
        return data_ret



class IQ_CH2(ParameterWithSetpoints):

    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._channel = channel

    def get_raw(self):
        time.sleep(0.2)
        data = self._instrument.get_data()
        if self._channel == 'I2':
            data_ret = data[0]
        elif self._channel == 'Q2':
            data_ret = data[1]
        else:
            print('Wrong parameter.')
        return data_ret



class ADC(Parameter):

    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._channel = channel

    def get_raw(self):
        time.sleep(0.2)
        data = self._instrument.get_data()
        if self._channel == 'CH1':
            data_ret = data[0]
        elif self._channel == 'CH2':
            data_ret = data[1]
        else:
            print('Wrong parameter.')
        return data_ret




class Redpitaya(VisaInstrument): 
    """
    QCoDeS driver for the Redpitaya
    """
    
    # all instrument constructors should accept **kwargs and pass them on to
    # super().__init__
    def __init__(self, name, address, **kwargs):
        # supplying the terminator means you don't need to remove it from every response
        super().__init__(name, address, terminator='\r\n', **kwargs)

        self.dummy_array_size_1 = 0
        self.dummy_array_size_2 = 2
        self.dummy_array_size_4 = 4
        
        
        self.add_parameter( name = 'freq_filter',  
                            #frequency of the low pass filter
                            label = 'Low pass filter cut-off freq',
                            vals = vals.Numbers(10e3,62.5e6),      
                            unit   = 'Hz',
                            set_cmd='FILTER:FREQ ' + '{:.12f}',
                            get_cmd='FILTER:FREQ?',
                            get_parser=float
                            )

        self.add_parameter( name = 'decimation_filter',
                            # number of decimated points  
                            label = 'Decimated points',
                            # unit   = 'Hz',
                            vals = vals.Numbers(10,65535),
                            set_cmd='FILTER:DEC ' + '{:.12f}',
                            get_cmd='FILTER:DEC?',
                            get_parser=int
                            )

        self.add_parameter( name = 'start_ADC',  
                            # Starting point of the ADC aquisition in second
                            label = 'Acquisition starting time',
                            unit   = 's',
                            vals = vals.Numbers(0,8191*8e-9),  #8192 is the maximum number of samples that can be generated (65 us)
                            set_cmd='ADC:STARTPOS '  + '{}',
                            get_cmd='ADC:STARTPOS?',
                            set_parser = self.get_samples_from_sec,
                            get_parser=self.get_sec_from_samples
                            )

        self.add_parameter( name = 'stop_ADC', 
                            #stopping point of the aquisition 
                            label = 'Acquisition stopping time',
                            unit   = 's',
                            vals = vals.Numbers(0,8191*8e-9),  #8192 is the maximum number of samples that can be generated (65 us)
                            set_cmd='ADC:STOPPOS ' + '{:.12f}',
                            get_cmd='ADC:STOPPOS?',
                            set_parser = self.get_samples_from_sec,
                            get_parser=self.get_sec_from_samples
                            )

        self.add_parameter( name = 'stop_DAC', 
                            #stopping point of the LUT (Look-Up Table) 
                            label = 'Stopping time of the LUT ',
                            unit   = 's',
                            vals = vals.Numbers(0,8192*8e-9),   #8192 is the maximum number of samples that can be generated (65 us)
                            set_cmd='DAC:STOPPOS ' + '{:.12f}',
                            get_cmd='DAC:STOPPOS?',
                            set_parser = self.get_samples_from_sec,
                            get_parser=self.get_sec_from_samples
                            )

        self.add_parameter( name = 'period',  
                            #period in second
                            label = 'Period',
                            unit  = 's',
                            vals = vals.Numbers(0,1),
                            set_cmd='PERIOD '+ '{}',
                            get_cmd='PERIOD?',
                            set_parser =self.get_samples_from_sec,
                            get_parser=self.get_sec_from_samples
                            )
  
        self.add_parameter( name = 'mode_output', 
                            # Mode(string) : 
                                        #'ADC': you get the rough uptput of the ADC: the entire trace
                                        #'IQCH1', you get I and Q from channel 1
                                        #'IQCH2', you get I and Q from channel 2
                                        #'IQLP1' you get I and Q after the low pass filter
                                        #'IQINT' you get I and Q after the integration
                                        #we can use either IQLP1 or IQINT for the low pass filtering
                            label = 'Output mode',
                            vals = vals.Enum('ADC', 'IQCH1', 'IQCH2', 'IQLP1', 'IQINT'),
                            set_cmd='OUTPUT:SELECT ' + '{}',
                            get_cmd='OUTPUT:SELECT?'
                            
                            #get_parser=float
                            )
        # The get command doesn't work, not clear why
        self.add_parameter( name = 'format_output', 
                            #Format(string) : 'BIN' or 'ASCII' 
                            label='Output format',
                            vals = vals.Enum('ASCII','BIN'),
                            set_cmd='OUTPUT:FORMAT ' + '{}',
                            get_cmd='OUTPUT:FORMAT?',
                            #snapshot_get  = False,
                            get_parser=str
                            )

        self.add_parameter('nb_measure',
                            set_cmd='{}',
                            get_parser=int,)
                            #initial_value = int(1) )

######################################################################
        self.add_parameter('status',
                           set_cmd='{}',
                           vals=vals.Enum('start', 'stop'),
                           set_parser = self.set_mode)

        self.add_parameter('data_size',
                           get_cmd='OUTPUT:DATASIZE?')


        self.add_parameter('data_output',
         					#get_cmd='OUTPUT:DATA?'
                            get_cmd = self.get_data)
                            #get_cmd = self.get_single_pulse)

        # self.add_parameter('data_output_raw',
        #                      get_cmd='OUTPUT:DATA?')


        self.add_parameter('pulse_zero',
                            set_cmd='{}',
                            #initial_value = int(0),
                            get_parser =  int)

        self.add_parameter('length_time', # total number of data points
                            set_cmd='{}',
                            get_parser =  int,)
                            #initial_value = int(0))


        self.add_parameter('pulse_axis',
                            unit='trace index',
                            label='Pulse-trace index axis',
                            parameter_class=GeneratedSetPoints,
                            startparam = self.pulse_zero,
                            stopparam=self.nb_measure,
                            numpointsparam=self.nb_measure,
                            snapshot_value = False,
                            vals=Arrays(shape=(self.nb_measure.get_latest,)))

        self.add_parameter('channel_axis',
                            unit = 'channel index',
                            label = 'Channel index axis for ADC power mode',
                            parameter_class = GeneratedSetPoints,
                            startparam = self.int_0,
                            stopparam = self.int_2,
                            numpointsparam = self.int_2,
                            snapshot_value = False,
                            vals=Arrays(shape=(self.dummy_array_size_2,)))


        self.add_parameter('time_axis',
                            unit='s',
                            label='Time',
                            parameter_class=GeneratedSetPoints,
                            startparam=self.pulse_zero,
                            stopparam=self.length_time,#*8*1e-9,
                            numpointsparam=self.length_time,
                            snapshot_value = False,
                            vals=Arrays(shape=(self.length_time.get_latest,)))#Maybe change the name to something understandable

        
        # ADC1/2 calls the class ADC which returns the signal either in channel 1 or channel 2.
        self.add_parameter('ADC1',
                            unit='V',
                            setpoints=(self.time_axis,),
                            label='Channel 1',
                            channel='CH1',
                            parameter_class=ADC,
                            vals=Arrays(shape=(self.length_time.get_latest,)))

        self.add_parameter('ADC2',
                            unit='V',
                            setpoints=(self.time_axis,),
                            label='Channel 2',
                            channel='CH2',
                            parameter_class=ADC,
                            vals=Arrays(shape=(self.length_time.get_latest,)))
 


        #I1/Q1/I2/Q2 calls the class ADC which returns the I/Q signal either in channel 1 or channel 2.
        self.add_parameter('I1',
                            unit='V',
                            setpoints=(self.time_axis,),
                            label='Raw I1',
                            channel='I1',
                            parameter_class=IQ_CH1,
                            vals=Arrays(shape=(self.length_time.get_latest,)))

        self.add_parameter('Q1',
                            unit='V',
                            setpoints=(self.time_axis,),
                            label='Raw Q1',
                            channel='Q1',
                            parameter_class=IQ_CH1,
                            vals=Arrays(shape=(self.length_time.get_latest,)))

        self.add_parameter('I2',
                            unit='V',
                            setpoints=(self.time_axis,),
                            label='Raw I2',
                            channel='I2',
                            parameter_class=IQ_CH2,
                            vals=Arrays(shape=(self.length_time.get_latest,)))

        self.add_parameter('Q2',
                            unit='V',
                            setpoints=(self.time_axis,),
                            label='Raw Q2',
                            channel='Q2',
                            parameter_class=IQ_CH2,
                            vals=Arrays(shape=(self.length_time.get_latest,)))



        #I1_INT/Q1_INT/I2_INT/Q2_INT calls the class ADC which returns the I_INT/Q_INT signal either in channel 1 or channel 2.

        self.add_parameter('I1_INT',
                            unit='V',
                            setpoints=(self.pulse_axis,),
                            label='Integrated I',
                            channel='I1',
                            parameter_class=IQ_INT,
                            vals=Arrays(shape=(self.nb_measure.get_latest,)))

        self.add_parameter('Q1_INT',
                            unit='V',
                            setpoints=(self.pulse_axis,),
                            label='Integrated I',
                            channel='Q1',
                            parameter_class=IQ_INT,
                            vals=Arrays(shape=(self.nb_measure.get_latest,)))

        self.add_parameter('I2_INT',
                            unit='V',
                            setpoints=(self.pulse_axis,),
                            label='Integrated I',
                            channel='I2',
                            parameter_class=IQ_INT,
                            vals=Arrays(shape=(self.nb_measure.get_latest,)))

        self.add_parameter('Q2_INT',
                            unit='V',
                            setpoints=(self.pulse_axis,),
                            label='Integrated I',
                            channel='Q2',
                            parameter_class=IQ_INT,
                            vals=Arrays(shape=(self.nb_measure.get_latest,)))

        self.add_parameter('IQ_INT_all',
                            unit='V',
                            label='Integrated I Q for both ADC',
                            channel='all_IQ',
                            parameter_class=IQ_INT_all,
                            vals=Arrays(shape=(tuple([self.nb_measure.get_latest,self.dummy_array_size_4]),)))

        ###########################We perform the average over the number of repeated traces

        self.add_parameter('I1_INT_AVG',
                            unit='V',
                            # setpoints=(self.nb_measure,),
                            label='Integrated averaged I',
                            channel='I1',
                            parameter_class=IQ_INT_AVG,
                            #snapshot_get  = False,
                            vals=Arrays(shape=(self.dummy_array_size_1,)))

        self.add_parameter('Q1_INT_AVG',
                            unit='V',
                            label='Integrated averaged Q',
                            channel='Q1',
                            parameter_class=IQ_INT_AVG,
                            #snapshot_get  = False,
                            vals=Arrays(shape=(self.dummy_array_size_1,)))

        self.add_parameter('I2_INT_AVG',
                            unit='V',
                            label='Integrated averaged I',
                            channel='I2',
                            parameter_class=IQ_INT_AVG,
                            #snapshot_get  = False,
                            vals=Arrays(shape=(self.dummy_array_size_1,)))

        self.add_parameter('Q2_INT_AVG',
                            unit='V',
                            label='Integrated averaged Q',
                            channel='Q2',
                            parameter_class=IQ_INT_AVG,
                            #snapshot_get  = False,
                            vals=Arrays(shape=(self.dummy_array_size_1,)))

        self.add_parameter('IQ_INT_AVG_all',
                            unit='V',
                            label='Integrated averaged I Q for both ADC',
                            channel='all_IQ',
                            parameter_class=IQ_INT_AVG_all,
                            #snapshot_get  = False,
                            vals=Arrays(shape=(self.dummy_array_size_4,)))

        self.add_parameter('ADC_power',
                            unit='W',
                            setpoints=(self.channel_axis,),
                            label='Integrated averaged power at both ADC',
                            channel='SpectrumAnalyzer',
                            parameter_class=ADC_power,
                            #snapshot_get  = False,
                            vals=Arrays(shape=(self.dummy_array_size_2,)))

        #It's a useful parameter to check the "ERR!" type errors.
        self.add_parameter('RESET',
                            get_cmd=self.reset)


        # good idea to call connect_message at the end of your constructor.
        # this calls the 'IDN' parameter that the base Instrument class creates 
        # for every instrument  which serves two purposes:
        # 1) verifies that you are connected to the instrument
        # 2) gets the ID info so it will be included with metadata snapshots later.
        self.connect_message()    

# ----------------------------------------------------- Methods -------------------------------------------------- #

#---------------------------------------------------------------------From seconds to samples and viceversa------

    def get_samples_from_sec(self, sec):
        samples=sec/8.0e-9
        samples=int(round(samples))
        time.sleep(0.1)
        return samples
        
    def get_sec_from_samples(self, samples):
        sec=float(samples)*8.0e-9
        time.sleep(0.1)
        return sec

#-------------------------------------------------------------Setting parameters
    def set_mode(self, mode):
        time.sleep(0.2)
        return mode

#------------------------------------------------------------Reset data output
    def reset(self):
        return self.ask('OUTPUT:DATA?')


#-------------------------------------------------------------------Look-Up-Table (LUT) menagement ---------

    def fill_LUT(self, function, parameters): 
        """
        Fill a LUT  
        Input:
                function(string): name of the function
                parameters(float): vector of parameters characterizing the function:
                freq (Hz), Amplitude (from 0 to 1), pulse_duration (s), delay (s)
        Output: 
                the table (int) 
        """
        if function == 'SIN': 
            freq, Amplitude, pulse_duration, delay = parameters
            if freq > 1./8e-9 or Amplitude > 1 or pulse_duration + delay >  8e-9*8192: 
                raise ValueError('One of the parameters is not correct in the sin LUT')
            else: 
                N_point = int(round(pulse_duration/8e-9))
                n_oscillation = freq*pulse_duration
                Amp_bit = Amplitude*8192                           ######### the DAC is 14 bit 8192 . The maximum aplitude will be (2^14)/2
                t = np.linspace(0, 2 * np.pi,N_point)
                return Amp_bit*np.concatenate((np.zeros(int(round(delay/8e-9))), np.sin(n_oscillation*t)))

        elif function == 'COS': 
            freq, Amplitude, pulse_duration, delay = parameters
            if freq > 1./8e-9 or Amplitude > 1 or pulse_duration + delay > 8e-9*8192: 
                raise ValueError('One of the parameters is not correct in the cos LUT')
            else: 
                N_point = int(round(pulse_duration/8e-9))
                n_oscillation = freq*pulse_duration
                
                Amp_bit = Amplitude*8192
                t = np.linspace(0,2*np.pi,N_point)
                return Amp_bit*np.concatenate((np.zeros(int(round(delay/8e-9))), np.cos(n_oscillation*t)))

        elif function == 'RAMSEY':

            freq, Amplitude, pulse_duration, t_wait, delay = parameters
            if freq > 1. / 8e-9 or Amplitude > 1 or 2*pulse_duration + delay + t_wait > 8e-9 * 8192:
                raise ValueError('One of the parameters is not correct is the Ramsey LUT')
            else :
                N_point = int(round(pulse_duration/8e-9))
                n_oscillation = freq * pulse_duration
                Amp_bit = Amplitude * 8192
                t = np.linspace(0, 2 * np.pi, N_point)
                wait_vec = np.zeros(int(round(t_wait/8e-9)))
                delay_vec = np.zeros(int(round(delay/8e-9)))
                excitation_vec = np.sin(n_oscillation*t)
                return Amp_bit*np.concatenate((delay_vec,excitation_vec,wait_vec,excitation_vec))

        elif function == 'ECHO':
            freq, Amplitude, pulse_pi_2, t_wait, delay = parameters
            if freq > 1. / 8e-9 or Amplitude > 1 or 4*pulse_pi_2 + delay + 2*t_wait > 8e-9 * 8192:
                raise ValueError('One of the parameters is not correct is the Echo LUT')
            else:
                N_point_pi_2 = int(round(pulse_pi_2/8e-9))
                N_point_pi = 2 * N_point_pi_2

                n_oscillation_pi_2 = freq * pulse_pi_2
                n_oscillation_pi = 2 * n_oscillation_pi_2

                Amp_bit = Amplitude * 8192
                t_pi_2 = np.linspace(0, 2 * np.pi, N_point_pi_2)
                t_pi = np.linspace(0, 2 * np.pi, N_point_pi)

                wait_vec = np.zeros(int(round(t_wait/8e-9)))
                delay_vec = np.zeros(int(round(delay/8e-9)))

                pi_2_vec = np.sin(n_oscillation_pi_2*t_pi_2)
                pi_vec = np.sin(n_oscillation_pi * t_pi)

                return Amp_bit*np.concatenate((delay_vec, pi_2_vec, wait_vec, pi_vec, wait_vec, pi_2_vec))
                
        elif function == 'STEP': 
            Amplitude, pulse_duration,t_slope,delay = parameters
            if Amplitude > 1 or pulse_duration + delay + 2*t_slope > 8e-9 * 8192: 
                raise ValueError('One of the parameters is not correct is the STEP LUT')
            
            Amp_bit = Amplitude*8192
            N_point = int(pulse_duration/8e-9)
            N_slope = int(t_slope/8e-9)
            N_delay = int(delay/8e-9)
            

            delay_vec = np.zeros(N_delay)
            slope_vec = np.linspace(0,1,N_slope)
            pulse_vec = np.ones(N_point)
            
            return Amp_bit*np.concatenate((delay_vec,slope_vec,pulse_vec,slope_vec[::-1]))
              
        else: 
            raise ValueError('This function is undefined')

    def send_DAC_LUT(self, table, channel, trigger = 'NONE'): 
        """
        Send a LUT to one of the DAC channels 
        Input: 
            - table (float): table to be sent 
            - channel(string): channel to which the table is sent 
            - trigger(string): send a trigger to the channels or not  
        Output: 
            None
        """
        self.log.info(__name__+ ' Send the DAC LUT \n')
        if trigger == 'NONE': 
            table_bit = table.astype(int) * 4  
        elif trigger == 'CH1': 
            table_bit = table.astype(int) * 4 + 1
        elif trigger == 'CH2': 
            table_bit = table.astype(int) * 4 + 2
        elif trigger == 'BOTH': 
            table_bit = table.astype(int) * 4 + 3
        else: 
            raise ValueError('Wrong trigger value')     

        table_bit = table_bit.astype(str)
        separator = ', '
        table_bit = separator.join(table_bit)
        if channel in ['CH1', 'CH2']: 
            time.sleep(0.1)
            #print(table_bit)
            self.write('DAC:' + channel + ' ' + table_bit)
        else: 
            raise ValueError('Wrong channel value')
                
    def send_IQ_LUT(self, table, channel, quadrature): 
        """
        Send a LUT to one of the IQ channel  (I and Q will be multiplied by the ADC input)
        Input: 
            - table (float): table to be sent 
            - channel(string): channel in which to table in sent 
            - trigger(string): send a trigger in channels or not 

        """
        self.log.info(__name__+ ' Send the IQ LUT \n')
        table_bit = table.astype(int) * 4 
        table_bit = table_bit.astype(str)
        separator = ', '
        table_bit = separator.join(table_bit)
        if quadrature in ['I', 'Q'] and channel in ['CH1', 'CH2']:
            time.sleep(0.1)
            self.write(quadrature + ':' + channel + ' ' + table_bit)
        else: 
            raise ValueError('Wrong quadrature or channel')

    def reset_LUT(self,time = 8192*8e-9): 
        """
        Reset all the LUT 
        Input: 
            time(float): duration of the table to be reset in second. 
            Default value is the all table 
        Output: 
            None
        """
        self.log.info(__name__+' Reset the DAC LUT \n')
        parameters = [0, 0, time,0]
        empty_table = self.fill_LUT('SIN',parameters)
        self.stop_DAC(time)
        self.send_DAC_LUT(empty_table,'CH1')
        self.send_DAC_LUT(empty_table,'CH2')
        self.send_IQ_LUT(empty_table,'CH1','I')
        self.send_IQ_LUT(empty_table,'CH1','Q')
        self.send_IQ_LUT(empty_table,'CH2','I')
        self.send_IQ_LUT(empty_table,'CH2','Q')

#--------------------------------------------------------------------------Output Data----

    def get_data(self):
        time.sleep(0.2)
        t = 0 
        nb_measure = self.nb_measure()
        mode = self.mode_output()
        N_single_trace = int(round(self.stop_ADC()/8e-9))-int(round(self.start_ADC()/8e-9))
        #print(1,t)
        # print(nb_measure, 'traces.', 'Mode:',mode)
        self.format_output('ASCII')
        self.status('start')
        time.sleep(0.2) # Timer to change if no time to start ; changed from 2
        signal = np.array([], dtype ='int32')
        t0 = time.time()

        while t < nb_measure:
            try:
                # time.sleep(0.0) ***testing
                rep = self.ask('OUTPUT:DATA?')
                #print(rep)
                #rep = self.data_output_raw()
                if rep[1] == '}':
                    print('Warning: fast polling')
                elif rep[1] != '0' or len(rep)<=2:  
                    print ('Memory problem %s' %rep[1])
                    #print(2,t)
                    #time.sleep(0.2)
                    self.status('stop')
                    #print(3,t)
                    #time.sleep(0.2)
                    self.status('start')
                else: 
                    # signal.append( rep[3:-1] + ',')
                    rep = eval( '[' + rep[3:-1] + ']' ) ### it creates an array of the data removing just the first one
                    signal = np.concatenate((signal,rep))
                    tick = np.bitwise_and(rep,3) # extraction du debut de l'aquisition: LSB = 3
                    t += len(np.where(tick[1:] - tick[:-1])[0])+1 # idex of the tick   
                    #print(t)
                    t1 = time.time()
                    #print (t1 - t0, t)
                    t0 = t1
            except: 
                t=t
        time.sleep(0.1)
        self.status('stop')
        #time.sleep(1)
        time.sleep(0.1)
        trash = self.ask('OUTPUT:DATA?')
        #time.sleep(1)
        #print(mode)
        if t > nb_measure: 
            #print(t, nb_measure)
            #print(tick)
            jump_tick = np.where(tick[1:] - tick[:-1])[0]
            #print(jump_tick)
            if len(jump_tick)==1:
                len_data_block = jump_tick[0]+1
            else:
                len_data_block = jump_tick[1] - jump_tick[0]

            signal = signal[:nb_measure*len_data_block]
            
        if (mode == 'ADC' or mode == 'IQCH1' or mode == 'IQCH2'):
            #print(12)
            data_1 = signal[::2]/(4*8192.)
            data_2 = signal[1::2]/(4*8192.)
            return data_1, data_2
        else: # mode IQint and IQLP1
            ICH1 = signal[::4]/(4*8192.)/N_single_trace#(self.length_time()/self.nb_measure()) # it staRT FROM 0 AND TAKE A POINT EVERY 4 
            QCH1 = signal[1::4]/(4*8192.)/N_single_trace#(self.length_time()/self.nb_measure()) # it staART FROM 1 AND TAKE A POINT EVERY 4
            ICH2 = signal[2::4]/(4*8192.)/N_single_trace#(self.length_time()/self.nb_measure())
            QCH2 = signal[3::4]/(4*8192.)/N_single_trace#(self.length_time()/self.nb_measure())
            return ICH1, QCH1, ICH2, QCH2
            
    def get_single_pulse(self):
        #self.mode_output(mode)
        self.format_output('ASCII')
        self.status('start')
        signal = np.array([], dtype ='int32')

        #Some sleep needed otherwise the data acquisition is too fast.
        time.sleep(0.8)
        rep = self.ask('OUTPUT:DATA?')
        if rep[1] != '0' or len(rep)<=2:
            print ('Memory problem %s' %rep[1])
            #print(2,t)
            self.status('stop')
            #print(3,t)
            self.status('start')
        else: 
            # signal.append( rep[3:-1] + ',')
            rep = eval( '[' + rep[3:-1] + ']' )
            signal = np.concatenate((signal,rep))
            tick = np.bitwise_and(rep,3) # extraction du debut de l'aquisition: LSB = 3
        self.status('stop')
        jump_tick = np.where(tick[1:] - tick[:-1])[0]
        len_data_block = jump_tick[1] - jump_tick[0]
        signal = signal[:len_data_block]

        print(self.mode_output())

        if self.mode_output() == ('ADC' or 'IQCH1' or 'IQCH2'):
            #print(self.mode_output())
            data_1 = signal[::2]/(4*8192.)
            data_2 = signal[1::2]/(4*8192.)
            return data_1, data_2
        else: 
            ICH1 = signal[::4]/(4*8192.)
            QCH1 = signal[1::4]/(4*8192.)
            ICH2 = signal[2::4]/(4*8192.)
            QCH2 = signal[3::4]/(4*8192.)
            return ICH1, QCH1, ICH2, QCH2

    def get_data_binary(self, mode, nb_measure):

        t = 0 
        self.set_mode_output(mode)
        self.set_format_output('BIN')
        self.start()
        signal = np.array([], dtype='int32')
        t0 = time.time()
        while t < nb_measure:
            try:
                rep = self.data_output_bin()
                if rep[0] != 0:
                    print ('Memory problem %s' %rep[0])
                    self.stop()
                    self.start()
                else: 
                    signal = np.concatenate((signal,rep[1:]))
                    if mode == ('ADC' or 'IQCH1' or 'IQCH2'): 
                        t = len(signal)/2
                    else: 
                        t = len(signal)/4
                t1 = time.time()
                print (t1 - t0, t)
                t0 = t1
            except: 
                t=t


        self.stop()
        trash = self.data_output()
            
        if mode == ('ADC' or 'IQCH1' or 'IQCH2'):
            data_1 = signal[::2][:nb_measure]/(4*8192.)
            data_2 = signal[1::2][:nb_measure]/(4*8192.)
            return data_1, data_2

        else:
            ICH1 = signal[::4][:nb_measure]/(4*8192.)
            QCH1 = signal[1::4][:nb_measure]/(4*8192.)
            ICH2 = signal[2::4][:nb_measure]/(4*8192.)
            QCH2 = signal[3::4][:nb_measure]/(4*8192.)
            return ICH1, QCH1, ICH2, QCH2     
    




    def int_0(self):
        return 0

    def int_2(self):
        return 2



    # def data_size(self):
    #     """
    #         Ask for the data size
    #     """ 
    #     #sleep(0.1)
    #     self.log.info(__name__ + ' Ask for the data size \n')
    #     #self.query('OUTPUT:DATASIZE?')
    #     self.write('OUTPUT:DATASIZE?')

        
    # def data_output(self):
    #     """
    #         Ask for the output data 
    #         Input:
    #             None
    #         Output: 
    #             - data: table of ASCII 
    #     """
    #     #sleep(0.2)
    #     self.log.info(__name__ + ' Ask for the output data \n')
    #     #data = self.query('OUTPUT:DATA?')
    #     data = self.write('OUTPUT:DATA?')
    #     return data


    # def get_data(self, mode, nb_measure):
    #     t = 0 
    #     self.mode_output(mode)
    #     self.format_output('ASCII')
    #     #self.start()
    #     self.status('start')
    #     signal = np.array([], dtype ='int32')
    #     t0 = time.time()

    #     while t < nb_measure:
    #         try:
    #             #time.sleep(0.1)
    #             rep = self.data_output()
    #             if rep[1] != '0' or len(rep)<=2:
    #                 print ('Memory problem %s' %rep[1])
    #                 self.status('stop')
    #                 self.status('start')
    #             else: 
    #                 # signal.append( rep[3:-1] + ',')
    #                 rep = eval( '[' + rep[3:-1] + ']' )
    #                 signal = np.concatenate((signal,rep))
    #                 tick = np.bitwise_and(rep,3) # extraction du debut de l'aquisition: LSB = 3
    #                 t += len(np.where(tick[1:] - tick[:-1])[0])+1 # idex of the tick   
    #                 # print t 
    #                 t1 = time.time()
    #                 print (t1 - t0, t)
    #                 t0 = t1
    #         except: 
    #             t=t
    #     #self.stop()
    #     self.status('stop')
            
    #     trash = self.data_output()
    #     # except: 
    #         # 'no trash'
    #     # i = 0 
    #     # while i==0: 
    #         # try: 
    #             # qt.msleep(0.25)
    #             # trash = self.data_output()
    #             # i = i +len(trash)
    #         # except: 
    #             # i = 0


    #     if t > nb_measure: 
    #         jump_tick = np.where(tick[1:] - tick[:-1])[0]
    #         len_data_block = jump_tick[1] - jump_tick[0]
    #         signal = signal[:nb_measure*len_data_block]
            
    #     if mode == ('ADC' or 'IQCH1' or 'IQCH2'):
    #         data_1 = signal[::2]/(4*8192.)
    #         data_2 = signal[1::2]/(4*8192.)
    #         print('OK')
    #         return data_1, data_2
    #     else: 
    #         ICH1 = signal[::4]/(4*8192.)
    #         QCH1 = signal[1::4]/(4*8192.)
    #         ICH2 = signal[2::4]/(4*8192.)
    #         QCH2 = signal[3::4]/(4*8192.)
    #         return ICH1, QCH1, ICH2, QCH2

    
    
        
        
        
        
