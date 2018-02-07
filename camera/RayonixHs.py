############################################################################
# This file is part of LImA, a Library for Image Acquisition
#
# Copyright (C) : 2009-2014
# European Synchrotron Radiation Facility
# BP 220, Grenoble 38043
# FRANCE
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
############################################################################
#=============================================================================
#
# file :        RayonixHs.py
#
# description : Python source for the RayonixHs and its commands. 
#                The class is derived from Device. It represents the
#                CORBA servant object which will be accessed from the
#                network. All commands which can be executed on the
#                Pilatus are implemented in this file.
#
# project :     TANGO Device Server
#
# copyleft :    European Synchrotron Radiation Facility
#               BP 220, Grenoble 38043
#               FRANCE
#
#=============================================================================
#         (c) - Bliss - ESRF
#=============================================================================
#
import PyTango
import sys, types, os, time

from Lima import Core
# import some useful helpers to create direct mapping between tango attributes
# and Lima interfaces.
from Lima.Server import AttrHelper

#==================================================================
#   RayonixHs Class Description:
#
#
#==================================================================

class RayonixHs(PyTango.Device_4Impl):

#--------- Add you global variables here --------------------------
    Core.DEB_CLASS(Core.DebModApplication, 'LimaCCDs')

#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def __init__(self,cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)

        # dictionnaries to be used with AttrHelper.get_attr_4u
        self.__FrameMode = {'SINGLE':RayonixHsAcq.SINGLE,
                           'FAST_TRANSFER':RayonixHsAcq.FAST_TRANSFER}

        self.__SignalType = {'OPTO': RayonixHsAcq.OPTO,
                                    'OPTO_INVERTED': RayonixHsAcq.OPTO_INVERTED,
                                    'CMOS': RayonixHsAcq.CMOS,
                                    'CMOS_PULLDOWN': RayonixHsAcq.CMOS_PULLDOWN,
                                    'CMOS_PULLUP': RayonixHsAcq.CMOS_PULLUP,
                                    'CMOS_PULLDOWN_INVERTED': RayonixHsAcq.CMOS_PULLDOWN_INVERTED,
                                    'CMOS_PULLUP_INVERTED': RayonixHsAcq.CMOS_PULLUP_INVERTED}
        self.__OutputSignalID = {'SHUTTER': RayonixHsAcq.ID_SHUTTER,
                           'INTEGRATE': RayonixHsAcq.ID_INTEGRATE,
                           'FRAME': RayonixHsAcq.ID_FRAME,
                           'LINE': RayonixHsAcq.ID_LINE,
                           'SHUTTER_OPENING': RayonixHsAcq.ID_SHUTTER_OPENING,
                           'SHUTTER_CLOSING': RayonixHsAcq.ID_SHUTTER_CLOSING,
                           'SHUTTER_ACTIVE': RayonixHsAcq.ID_SHUTTER_ACTIVE,
                           'TRIGGER_RISE_WAIT': RayonixHsAcq.ID_TRIGGER_RISE_WAIT,
                           'TRIGGER_RISE_ACK': RayonixHsAcq.ID_TRIGGER_RISE_ACK,
                           'TRIGGER_FALL_WAIT': RayonixHsAcq.ID_TRIGGER_FALL_WAIT,
                           'TRIGGER_FALL_ACK': RayonixHsAcq.ID_TRIGGER_FALL_ACK,                           
                           'TRIGGER_2_RISE_WAIT': RayonixHsAcq.ID_TRIGGER_2_RISE_WAIT,
                           'TRIGGER_2_RISE_ACK': RayonixHsAcq.ID_TRIGGER_2_RISE_ACK,
                           'INPUT_FRAME': RayonixHsAcq.ID_INPUT_FRAME,
                           'INPUT_GATE': RayonixHsAcq.ID_INPUT_GATE,
                           }
        self___OutputChannel = {'CHAN1': RayonixHsAcq.CHANNEL_1,
                             'CHAN2': RayonixHsAcq.CHANNEL_2
                             }
        self.__Cooler = {'START': True,
                         'STOP': False}
        self.__VacuumValve = {'OPEN': True,
                              'CLOSE': False}
        self.__ElectronicShutterEnabled = {'TRUE': True,
                                           'FALSE': False}

        self.__NewBackgroundNeeded = {'YES': True,
                                      'NO': False}

        self.__FrameTriggerSignalType = self.__SignalType
        self.__SequenceGateSignalType = self.__SignalType
        self.__OutputSignalType = self.__SignalType
        self.__ReadoutMode = {'READOUT_MODE_STANDARD': RayonixHsAcq.READOUT_MODE_STANDARD,
                              'READOUT_MODE_HIGH_GAIN': RayonixHsAcq.READOUT_MODE_HIGH_GAIN,
                              'READOUT_MODE_LOW_NOISE': RayonixHsAcq.READOUT_MODE_LOW_NOISE,
                              'READOUT_MODE_HDR32': RayonixHsAcq.READOUT_MODE_HDR32,
                              'READOUT_MODE_TURBO': RayonixHsAcq.READOUT_MODE_TURBO,
                              'READOUT_MODE_HDR16': RayonixHsAcq.READOUT_MODE_HDR16
                              }
        self.__Attribute2FunctionBase = {'frame_mode': 'FrameMode',
                                         'frame_trigger_signal_type': 'FrameTriggerSignalType',
                                         'sequence_gate_signal_type': 'SequenceGateSignalType',
                                         'electronic_shutter_enabled': 'ElectronicShutterEnabled',
                                         'cooler_temperature_setpoint': 'CoolerTemperatureSetpoint',
                                         'sensor_temperature_setpoint': 'SensorTemperatureSetpoint',
                                         'sensor_temperature': 'SensorTemperature',
                                         'cooler': 'Cooler',
                                         'vacuum_valve': 'VacuumValve',
                                         'new_background_needed': 'NewBackgroundNeeded',
                                         'readout_mode': 'ReadoutMode',
                                         }
        self.__OtherAttribute2FunctionBase = {'output1_signal_type': 'OutputSignalType',
                                              'output2_signal_type': 'OutputSignalType',
                                              'output1_id': 'OutputSignalID',
                                              'output2_id': 'OutputSignalID'
                                              }
        self.init_device()

                                               
#------------------------------------------------------------------
#    Device destructor
#------------------------------------------------------------------
    def delete_device(self):
        pass


#------------------------------------------------------------------
#    Device initialization
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def init_device(self):
        self.set_state(PyTango.DevState.ON)

        # Load the properties
        self.get_device_properties(self.get_device_class())

        # Apply properties if any
        if self.frame_mode:
            self.applyNewPropery('frame_mode')
        
        if self.frame_trigger_signal_type:
            self.applyNewPropery('frame_trigger_signal_type')

        if self.sequence_gate_signal_type:
            self.applyNewPropery('sequence_gate_signal_type')
        
        if self.electronic_shutter_enabled:
            self.applyNewPropery('electronic_shutter_enabled')

        if self.output1_signal_type:
            self.applyNewPropery('electronic_shutter_enabled')

        if self.electronic_shutter_enabled:
            self.applyNewPropery('electronic_shutter_enabled')

        if self.cooler_temperature_setpoint:
            _RayonixHsInterface.setCoolerTemperatureSetpoint(self.cooler_temperature_setpoint)

        if self.sensor_temperature_setpoint:
            _RayonixHsInterface.setSensorTemperatureSetpoint(self.sensor_temperature_setpoint)

        if self.output1_signal_type:
            self.applyNewPropery('output1_signal_type', RayonixHsAcq.CHANNEL_1)

        if self.output2_signal_type:
            self.applyNewPropery('output2_signal_type', RayonixHsAcq.CHANNEL_2)

        if self.output1_id:
            self.applyNewPropery('output1_id', RayonixHsAcq.CHANNEL_1)

        if self.output2_id:
            self.applyNewPropery('output1_id', RayonixHsAcq.CHANNEL_2)

                
    @Core.DEB_MEMBER_FUNCT
    def applyNewPropery(self, prop_name, extra=None):
        if extra is not None: name = self.__OtherAttribute2FunctionBase[prop_name]
        else: name = self.__Attribute2FunctionBase[prop_name]
                                           
        dict = getattr(self, '_'+self.__class__.__name__+'__'+name)
        func = getattr(_RayonixHsInterface, 'set'+name)
        key = getattr(self, prop_name)
        val = AttrHelper.getDictValue(dict, key.upper())
        if  val is None:
            deb.Error('Wrong value for property %s :%s' % (prop_name, val))
        else:
            if extra is not None: func(extra,val)
            else: func(val)

            
            
           
            

#==================================================================
#
#    RayonixHs read/write attribute methods
#
#==================================================================


    def __getattr__(self,name) :
        return AttrHelper.get_attr_4u(self, name, _RayonixHsInterface)


    ## @brief return the ID on output channel #1
    #  
    @Core.DEB_MEMBER_FUNCT
    def read_output1_id(self, attr):        
        id = _RayonixHsInterface.getOutputSignalID(RayonixHsAcq.CHANNEL_1)
        val = AttrHelper.getDictKey(self.__OutputSignalID, id)
        attr.set_value(val)        
        
    ## @brief write the ID on output channel #1
    #  
    @Core.DEB_MEMBER_FUNCT
    def write_output1_id(self, attr):
        id = attr.get_write_value()
        val = AttrHelper.getDictValue(self.__OutputSignalID, id)
        _RayonixHsInterface.setOutputSignalID(RayonixHsAcq.CHANNEL_1, val)

    ## @brief return the ID on output channel #2
    #  
    @Core.DEB_MEMBER_FUNCT
    def read_output2_id(self, attr):        
        id = _RayonixHsInterface.getOutputSignalID(RayonixHsAcq.CHANNEL_2)
        val = AttrHelper.getDictKey(self.__OutputSignalID, id)
        attr.set_value(val)        
        
    ## @brief write the ID on output channel #2
    #  
    @Core.DEB_MEMBER_FUNCT
    def write_output2_id(self, attr):
        id = attr.get_write_value()
        val = AttrHelper.getDictValue(self.__OutputSignalID, id)
        _RayonixHsInterface.setOutputSignalID(RayonixHsAcq.CHANNEL_2, val)

    ## @brief return the signal type on output channel #1
    #  
    @Core.DEB_MEMBER_FUNCT
    def read_output1_signal_type(self, attr):        
        sig_type = _RayonixHsInterface.getOutputSignalType(RayonixHsAcq.CHANNEL_1)
        val = AttrHelper.getDictKey(self.__OutputSignalType, sig_type)
        attr.set_value(val)        
        
    ## @brief write the signal type  on output channel #1
    #  
    @Core.DEB_MEMBER_FUNCT
    def write_output1_signal_type(self, attr):
        sig_type = attr.get_write_value()
        val = AttrHelper.getDictValue(self.__OutputSignalType, sig_type)
        _RayonixHsInterface.setOutputSignalType(RayonixHsAcq.CHANNEL_1, val)

    ## @brief return the signal type on output channel #2
    #  
    @Core.DEB_MEMBER_FUNCT
    def read_output2_signal_type(self, attr):        
        sig_type = _RayonixHsInterface.getOutputSignalType(RayonixHsAcq.CHANNEL_2)
        val = AttrHelper.getDictKey(self.__OutputSignalType, sig_type)
        attr.set_value(val)        
        
    ## @brief write the signal type  on output channel #2
    #  
    @Core.DEB_MEMBER_FUNCT
    def write_output2_signal_type(self, attr):
        sig_type = attr.get_write_value()
        val = AttrHelper.getDictValue(self.__OutputSignalType, sig_type)
        _RayonixHsInterface.setOutputSignalType(RayonixHsAcq.CHANNEL_2, val)


#==================================================================
#
#    RayonixHs command methods
#
#==================================================================

#------------------------------------------------------------------
#    getAttrStringValueList command:
#
#    Description: return a list of authorized values if any
#    argout: DevVarStringArray   
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def getAttrStringValueList(self, attr_name):
        if attr_name in ['output1_id','output2_id']:
            return list(self.__OutputSignalID.keys())
        elif attr_name in ['output1_signal_type', 'output2_signal_type']:
            return list(self.__OutputSignalType.keys())
        else:
            return AttrHelper.get_attr_string_value_list(self, attr_name)
    
    @Core.DEB_MEMBER_FUNCT
    def acquireNewBackground(self, params):
        _RayonixHsInterface.acquireNewBackground(params[0], params[1])

#==================================================================
#
#    RayonixHs class definition
#
#==================================================================
class RayonixHsClass(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {
        }

    #    Device Properties
    device_property_list = {
        'frame_mode':
        [PyTango.DevString,
         'Frame Transfer mode', ['single']],
        'frame_trigger_signal_type':
        [PyTango.DevString,
         'Frame trigger (input 1) signal type', ['opto']],
        'sequence_gate_signal_type':
        [PyTango.DevString,
         'Sequence gate (input 2) signal type', ['opto']],
        'electronic_shutter_enabled':
        [PyTango.DevString,
         'Electronic shutter enabled', ['false']],
        'cooler_temperature_setpoint':
        [PyTango.DevDouble,
         'Detector cooling setpoint', [-120]],
        'sensor_temperature_setpoint':
        [PyTango.DevDouble,
         'Sensor temperature setpoint', [-80]],
        'output1_signal_type':
        [PyTango.DevString,
         'Output channel #1 signal type', ['opto']],
        'output2_signal_type':
        [PyTango.DevString,
         'Output channel #2 signal type', ['opto']],
        'output1_id':
        [PyTango.DevString,
         'Output channel #1 ID', ['shutter']],
        'output2_id':
        [PyTango.DevString,
         'Output channel #2 ID', ['frame']],
        }

    #    Command definitions
    cmd_list = {
        'getAttrStringValueList':
        [[PyTango.DevString, "Attribute name"],
         [PyTango.DevVarStringArray, "Authorized String value list"]],
	'acquireNewBackground':
	[[PyTango.DevVarLongArray, "[0]:0/1 blocking, [1]: nb_background"],
	 [PyTango.DevVoid]],
        }


    #    Attribute definitions
    attr_list = {
        'frame_mode':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Frame Transfer mode',
             'unit': 'SINGLE/FAST_TRANSFER',
             }],
        'frame_trigger_signal_type':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Frame trigger (input 1) signal type',
             'unit': 'OPTO/OPTO_INVERTED/CMOS/CMOS_PULLDOWN/CMOS_PULLUP/CMOS_PULLDOWN_INVERTED/CMOS_PULLUP_INVERTED',
             }],
                
        'sequence_gate_signal_type':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Sequence gate (input 2) signal type',
             'unit': 'OPTO/OPTO_INVERTED/CMOS/CMOS_PULLDOWN/CMOS_PULLUP/CMOS_PULLDOWN_INVERTED/CMOS_PULLUP_INVERTED',
             }],
                
        'electronic_shutter_enabled':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Electronic shutter enabled',
             'unit': 'TRUE/FALSE',
             }],                
        'cooler_temperature_setpoint':
        [[PyTango.DevDouble,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Detector cooling setpoint',
             'unit': 'deg. Celcius',
             }],                
        'sensor_temperature_setpoint':
        [[PyTango.DevDouble,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Sensor temperature setpoint',
             'unit': 'deg. Celcius',
             }],
        'sensor_temperature':
        [[PyTango.DevDouble,
          PyTango.SCALAR,
          PyTango.READ],
         {
             'label':'Detector Sensor temperature',
             'unit': 'deg. Celcius',
             }],
        'cooler':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Detector cooling',
             'unit': 'START/STOP',
             }],
        'vacuum_valve':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Vacuum valve',
             'unit': 'OPEN/CLOSE',
             }],
        'output1_signal_type':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Output channel #2 signal type',
             'unit': 'OPTO/OPTO_INVERTED/CMOS/CMOS_PULLDOWN/CMOS_PULLUP/CMOS_PULLDOWN_INVERTED/CMOS_PULLUP_INVERTED',
             }],
        'output2_signal_type':
            [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Output channel #2 signal type',
             'unit': 'OPTO/OPTO_INVERTED/CMOS/CMOS_PULLDOWN/CMOS_PULLUP/CMOS_PULLDOWN_INVERTED/CMOS_PULLUP_INVERTED',
             }],
        'output1_id':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Output channel #1 ID',
             'unit': 'SHUTTER/INTEGRATE/FRAME/LINE/SHUTTER_OPENING/SHUTTER_CLOSING/SHUTTER_ACTIVE/TRIGGER_RISE_WAIT/TRIGGER_RISE_ACK/TRIGGER_FALL_WAIT/TRIGGER_FALL_ACK/TRIGGER_2_RISE_WAIT/TRIGGER_2_RISE_ACK/INPUT_FRAME/INPUT_GATE',
             }],
        'output2_id':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':'Output channel #2 ID',
             'unit': 'SHUTTER/INTEGRATE/FRAME/LINE/SHUTTER_OPENING/SHUTTER_CLOSING/SHUTTER_ACTIVE/TRIGGER_RISE_WAIT/TRIGGER_RISE_ACK/TRIGGER_FALL_WAIT/TRIGGER_FALL_ACK/TRIGGER_2_RISE_WAIT/TRIGGER_2_RISE_ACK/INPUT_FRAME/INPUT_GATE',
             }],
	'new_background_needed':
	[[PyTango.DevString,
	  PyTango.SCALAR,
	  PyTango.READ],
     	 {
	     'label':'background is needed',
	     'unit': 'True or False', 
         }],
        'readout_mode':
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ_WRITE],
          {
                'label': 'Readout mode',
                'unit': 'READOUT_MODE_STANDARD/READOUT_MODE_HIGH_GAIN/READOUT_MODE_LOW_NOISE/READOUT_MODE_HDR/READOUT_MODE_TURBO',
           }],
        }

#------------------------------------------------------------------
#    RayonixHsClass Constructor
#------------------------------------------------------------------
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name)

            
#----------------------------------------------------------------------------
#                              Plugins
#----------------------------------------------------------------------------
from Lima  import RayonixHs as RayonixHsAcq

_RayonixHsCamera = None
_RayonixHsInterface = None

def get_control(**keys) :
    #properties are passed here as string
    global _RayonixHsCamera
    global _RayonixHsInterface
    if _RayonixHsCamera is None:
        print('\n\nStarting and configuring the RayonixHs camera ...')
        _RayonixHsCamera = RayonixHsAcq.Camera()
        _RayonixHsInterface = RayonixHsAcq.Interface(_RayonixHsCamera)
        print('\n\nRayonixHs Camera (%s:%s) is started'%(_RayonixHsCamera.getDetectorType(),_RayonixHsCamera.getDetectorModel()))
    return Core.CtControl(_RayonixHsInterface)

    
def get_tango_specific_class_n_device():
    return RayonixHsClass,RayonixHs

