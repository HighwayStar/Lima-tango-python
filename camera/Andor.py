############################################################################
# This file is part of LImA, a Library for Image Acquisition
#
# Copyright (C) : 2009-2016
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
# file :        Andor.py
#
# description : Python source for the Andor and its commands. 
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
from Lima import Andor as AndorModule
# import some useful helpers to create direct mapping between tango attributes
# and Lima interfaces.
from Lima.Server import AttrHelper

class Andor(PyTango.Device_4Impl):

    Core.DEB_CLASS(Core.DebModApplication, 'LimaCCDs')
    
#==================================================================
#   Andor Class Description:
#
#
#==================================================================

class Andor(PyTango.Device_4Impl):

#--------- Add you global variables here --------------------------
    Core.DEB_CLASS(Core.DebModApplication, 'LimaCCDs')

#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def __init__(self,cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)

        # dictionnaries to be used with AttrHelper.get_attr_4u
        self.__FastExtTrigger = {'ON':True,
                           'OFF':False}
        self.__Cooler = {'ON': True,
                             'OFF': False}
        self.__ShutterLevel = {'LOW':0,
                                   'HIGH':1}       

        if _AndorInterface.getFanMode() == AndorAcq.FAN_UNSUPPORTED:
            self.__FanMode = {'UNSUPPORTED': AndorAcq.FAN_UNSUPPORTED}
        else:
            self.__FanMode = {'FULL': AndorAcq.FAN_ON_FULL,
                              'LOW': AndorAcq.FAN_ON_LOW,
                              'OFF': AndorAcq.FAN_OFF,
                              }

        if _AndorInterface.getHighCapacity() == AndorAcq.HC_UNSUPPORTED:
            self.__HighCapacity = {'UNSUPPORTED': AndorAcq.HC_UNSUPPORTED}
        else:
            self.__HighCapacity = {'HIGH_CAPACITY': AndorAcq.HIGH_CAPACITY,
                                   'HIGH_SENSITIVITY': AndorAcq.HIGH_SENSITIVITY,
                                   }

        if _AndorInterface.getBaselineClamp() == AndorAcq.BLCLAMP_UNSUPPORTED:
            self.__BaselineClamp = {'UNSUPPORTED': AndorAcq.BLCLAMP_UNSUPPORTED}
        else:
            self.__BaselineClamp = {'ON': AndorAcq.BLCLAMP_ENABLED,
                                    'OFF': AndorAcq.BLCLAMP_DISABLED}

        #Only needed to map attribute and function which does not fit the with naming convention.
        self.__Attribute2FunctionBase = {
            'temperature_sp': 'TemperatureSP',
            #'my_attr1': 'AnOtherFunctionName',
                                       }

        # prepare lists of supported PGain/VerticalShiftSpeed/AdcSpeed
        self.__PGain = {}
        max_ind = _AndorInterface.getPGainMaxIndex()
        for ind in range(max_ind):
            self.__PGain[_AndorInterface.getPGainString(ind)] = ind
        
        self.__VsSpeed = {}
        max_ind = _AndorInterface.getVsSpeedMaxIndex()
        for ind in range(max_ind):
            self.__VsSpeed[_AndorInterface.getVsSpeedString(ind)] = ind

        self.__AdcSpeed = {}
        max_ind = _AndorInterface.getAdcSpeedMaxIndex()
        for ind in range(max_ind):
            self.__AdcSpeed[_AndorInterface.getAdcSpeedPaireString(ind)] = ind
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
        if self.p_gain:
            _AndorInterface.setPGain(self.__PGain[self.p_gain])
            
        if self.vs_speed:
            _AndorInterface.setVsSpeed(self.__VsSpeed[self.vs_speed])
            
        if self.adc_speed:
            _AndorInterface.setAdcSpeed(self.__AdcSpeed[self.adc_speed])

        if self.temperature_sp:            
            _AndorInterface.setTemperatureSP(self.temperature_sp)
            
        if self.cooler:
            _AndorInterface.setCooler(self.__Cooler[self.cooler])
            
        if self.fast_ext_trigger:
            _AndorInterface.setFastExtTrigger(self.__FastExtTrigger[self.fast_ext_trigger])
            
        if self.shutter_level:
            _AndorInterface.setShutterLevel(self.__ShutterLevel[self.shutter_level])


        if 'UNSUPPORTED' in self.__FanMode and self.fan_mode:
            deb.Error('Cannot set fan_mode property, not supported for this camera model')
        elif self.fan_mode:
                _AndorInterface.setFanMode(self.__FanMode[self.fan_mode])

        if 'UNSUPPORTED' in self.__HighCapacity and self.high_capacity:
            deb.Error('Cannot set high_capacity property, not supported for this camera model')
        elif self.high_capacity:
                _AndorInterface.setHighCapacity(self.__HighCapacity[self.high_capacity])

        if 'UNSUPPORTED' in self.__BaselineClamp and self.baseline_clamp:
            deb.Error('Cannot set baseline_clamp propery, not supported for this camera model')
        elif self.baseline_clamp:
            _AndorInterface.setBaselineClamp(self.__BaselineClamp[self.baseline_clamp])

 
        

#==================================================================
#
#    Andor read/write attribute methods
#
#==================================================================


    def __getattr__(self,name) :
        return AttrHelper.get_attr_4u(self, name, _AndorInterface)


    ## @brief return the timing times, exposure and latency
    #  
    def read_timing(self, attr):
        timing=[]
        timing.append(_AndorCamera.getExpTime())
        timing.append(_AndorCamera.getLatTime())
        
        attr.set_value(timing,2)        
        

#==================================================================
#
#    Andor command methods
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
        return AttrHelper.get_attr_string_value_list(self, attr_name)
    

#==================================================================
#
#    Andor class definition
#
#==================================================================
class AndorClass(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {
        }

    #    Device Properties
    device_property_list = {
        'config_path':
        [PyTango.DevString,
         'configuration path directory', []],
        'camera_number':
        [PyTango.DevShort,
         'Camera number', []],
        'p_gain':
        [PyTango.DevString,
         'Preamplifier gain', []],
        'vs_speed':
        [PyTango.DevString,
         'Vertical shift speed', []],
        'adc_speed':
        [PyTango.DevString,
         'ADC/HSspeed pairs', []],
        'temperature_sp':
        [PyTango.DevShort,
         'Temperature set point in Celsius', []],
        'cooler':
        [PyTango.DevString,
         'Start or stop the cooler ("ON"/"OFF")', []],
        'fast_ext_trigger':
        [PyTango.DevString,
         'Trigger fast mode ("ON"/"OFF")', []],
        'shutter_level':
        [PyTango.DevString,
         'level of the shutter output ("LOW"/"HIGH")', []],                 
        'fan_mode':
        [PyTango.DevString,
         'Fan mode ("FAN_ON_FULL"/"ON_LOW"/"FAN_OFF")',[]],
        'high_capacity': 
        [PyTango.DevString,
         'High Capacity ("HIGH_CAPACITY"/"HIGH_SENSITIVITY")',[]],
        'baseline_clamp': 
        [PyTango.DevString,
         'baseline clamp  ("ON"/"OFF")',[]],
        }


    #    Command definitions
    cmd_list = {
        'getAttrStringValueList':
        [[PyTango.DevString, "Attribute name"],
         [PyTango.DevVarStringArray, "Authorized String value list"]]
        }


    #    Attribute definitions
    attr_list = {
        'fast_ext_trigger':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'unit': 'N/A',
             'format': '',
             'description': 'Fast trigger mode, see manual for usage, OFF or ON',
             }],
        'shutter_level':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'unit': 'N/A',
             'format': '',
             'description': 'Shutter output level, see manual for usage LOW or HIGH',
             }],
       'temperature_sp':
        [[PyTango.DevShort,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'unit': 'C',
             'format': '%1d',
             'description': 'in Celsius',
             }],
        'temperature':
        [[PyTango.DevShort,
          PyTango.SCALAR,
          PyTango.READ],
         {
             'unit': 'C',
             'format': '%1d',
             'description': 'in Celsius',
             }],
        'cooler':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'unit': 'N/A',
             'format': '',
             'description': 'Start/stop the cooler, OFF or ON',
             }],
        'cooling_status':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ],
         {
             'label':'Cooling status',
             'unit': 'N/A',
             'format': '%1d',
             'description': 'return status of the cooling system, tell if the setpoint is reached',
             }],
        'timing':
        [[PyTango.DevFloat,
          PyTango.SPECTRUM,
          PyTango.READ,2],
        {
             'unit': 'second',
             'format': '%f',
             'description': '[0]: exposure, [1]: latency',
             }],
        'p_gain':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'unit': 'N/A',
             'format': '%s',
             'description': 'Premplifier Gain which can be apply to the readout, from X1-XN, check the camera documentation for the valid range',
             }],
        'vs_speed':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'unit': 'N/A',
             'format': '',
             'description': 'Vertical shift speed,  in us/pixel, check the camera documentation for the valid range',
             }],
        'adc_speed':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'unit': 'N/A',
             'format': '',
             'description': 'ADC and Horizontal shift speed, in ADCchannel/Freq.Mhz, check the documentatio for more help',
             }],
        'high_capacity':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'unit': 'N/A',
             'format': '',
             'description': 'HIGH_CAPACITY or HIGH_SENSITIVITY',
             }],
        'fan_mode':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'unit': 'N/A',
             'format': '',
             'description': 'FAN_OFF or FAN_ON_FULL, or FAN_ON_LOW',
             }],
        'baseline_clamp':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'unit': 'N/A',
             'format': '',
             'description': 'ON or OFF',
             }],

        }

#------------------------------------------------------------------
#    AndorClass Constructor
#------------------------------------------------------------------
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name)

            
#----------------------------------------------------------------------------
#                              Plugins
#----------------------------------------------------------------------------
from Lima  import Andor as AndorAcq

_AndorCamera = None
_AndorInterface = None

def get_control(config_path='/usr/local/etc/andor', camera_number = '0',**keys) :
    #properties are passed here as string
    global _AndorCamera
    global _AndorInterface
    if _AndorCamera is None:
        print('\n\nStarting and configuring the Andor camera ...')
        _AndorCamera = AndorAcq.Camera(config_path, int(camera_number))
        _AndorInterface = AndorAcq.Interface(_AndorCamera)
        print('\n\nAndor Camera #%s (%s:%s) is started'%(camera_number,_AndorCamera.getDetectorType(),_AndorCamera.getDetectorModel()))
    return Core.CtControl(_AndorInterface)

    
def get_tango_specific_class_n_device():
    return AndorClass,Andor

