############################################################################
# This file is part of LImA, a Library for Image Acquisition
#
# Copyright (C) : 2009-2015
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
##############################################################################
## license :
##============================================================================
##
## File :        Merlin.py
## 
## Project :     Merlin: A Medipix3RX Quad readout
##
## This file is part of Tango device class.
## 
## Tango is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Tango is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with Tango.  If not, see <http://www.gnu.org/licenses/>.
## 
##
##############################################################################

import PyTango
import sys
from Lima import Core
from Lima import Merlin as MerlinAcq
from Lima.Server import AttrHelper

class Merlin (PyTango.Device_4Impl):

    Core.DEB_CLASS(Core.DebModApplication, 'LimaCCDs')
    
    def __init__(self,cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)
        Merlin.init_device(self)

        self.__Switch = {'OFF': MerlinAcq.Camera.OFF,
                         'ON': MerlinAcq.Camera.ON}

        self.__ColourMode = {'MONOCHROME': MerlinAcq.Camera.Monochrome,
                             'COLOUR': MerlinAcq.Camera.Colour}
        
        self.__Counter = {'COUNTER0': MerlinAcq.Camera.COUNTER0,
                          'COUNTER1': MerlinAcq.Camera.COUNTER1,
                          'BOTH': MerlinAcq.Camera.BOTH}
        
        self.__Depth = {'BPP1': MerlinAcq.Camera.BPP1,
                        'BPP6': MerlinAcq.Camera.BPP6,
                        'BPP12': MerlinAcq.Camera.BPP12,
                        'BPP24': MerlinAcq.Camera.BPP24}
        
        self.__GainSetting = {'SLGM': MerlinAcq.Camera.SLGM,
                              'LGM': MerlinAcq.Camera.LGM,
                              'HGM': MerlinAcq.Camera.HGM, 
                              'SHGM': MerlinAcq.Camera.SHGM}

        self.__Trigger = {'INTERNAL': MerlinAcq.Camera.INTERNAL,
                          'RISING_EDGE_TTL': MerlinAcq.Camera.RISING_EDGE_TTL,
                          'FALLING_EDGE_TTL': MerlinAcq.Camera.FALLING_EDGE_TTL,
                          'RISING_EDGE_LVDS': MerlinAcq.Camera.RISING_EDGE_LVDS,
                          'FALLING_EDGE_LVDS': MerlinAcq.Camera.FALLING_EDGE_LVDS,
                          'SOFT': MerlinAcq.Camera.SOFT}
        
        self.__TriggerOutput = {'TTL': MerlinAcq.Camera.TTL,
                                'LVDS': MerlinAcq.Camera.LVDS,
                                'TTL_DELAYED': MerlinAcq.Camera.TTL_DELAYED,
                                'LVDS_DELAYED': MerlinAcq.Camera.LVDS_DELAYED,
                                'FOLLOW_SHUTTER': MerlinAcq.Camera.FOLLOW_SHUTTER,
                                'ONE_PER_ACQ_BURST': MerlinAcq.Camera.ONE_PER_ACQ_BURST,
                                'SHUTTER_AND_SENSOR_READ': MerlinAcq.Camera.SHUTTER_AND_SENSOR_READ,
                                'OUTPUT_BUSY': MerlinAcq.Camera.OUTPUT_BUSY}

        self.__TriggerLevel = {'NORMAL': MerlinAcq.Camera.NORMAL,
                               'INVERTED': MerlinAcq.Camera.INVERTED}

        self.__FillMode = {'NOFILL' : MerlinAcq.Camera.NOFILL,
                           'INSERTZERO' : MerlinAcq.Camera.INSERTZERO,
                           'DISTRIBUTE' : MerlinAcq.Camera.DISTRIBUTE,
                           'INTERPOLATE' : MerlinAcq.Camera.INTERPOLATE}

        self.init_device()

        
    def delete_device(self):
        pass

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)        


    #-----------------------------------------------------------------------------
    #    Merlin read/write attribute methods
    #-----------------------------------------------------------------------------
    
    @Core.DEB_MEMBER_FUNCT
    def read_softwareVersion(self, attr):
        attr.set_value(_MerlinCamera.getSoftwareVersion())
        
    @Core.DEB_MEMBER_FUNCT
    def read_chargeSumming(self, attr):
        mode = _MerlinCamera.getChargeSumming()
        attr.set_value(AttrHelper.getDictKey(self.__Switch,mode))
        
    @Core.DEB_MEMBER_FUNCT
    def write_chargeSumming(self, attr):
        data=attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__Switch,data)
        _MerlinCamera.setChargeSumming(mode)
        
    @Core.DEB_MEMBER_FUNCT
    def read_colourMode(self, attr):
        mode = _MerlinCamera.getColourMode()
        attr.set_value(AttrHelper.getDictKey(self.__ColourMode,mode))
        
    @Core.DEB_MEMBER_FUNCT
    def write_colourMode(self, attr):
        data=attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__ColourMode,data)
        _MerlinCamera.setColourMode(mode)
        
    @Core.DEB_MEMBER_FUNCT
    def read_continuousRW(self, attr):
        mode = _MerlinCamera.getContinuousRW()
        attr.set_value(AttrHelper.getDictKey(self.__Switch,mode))
        
    @Core.DEB_MEMBER_FUNCT
    def write_continuousRW(self, attr):
        data=attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__Switch,data)
        _MerlinCamera.setContinuousRW(mode)
        
    @Core.DEB_MEMBER_FUNCT
    def read_counter(self, attr):
        counter = _MerlinCamera.getEnableCounters()
        attr.set_value(AttrHelper.getDictKey(self.__Counter,counter))
        
    @Core.DEB_MEMBER_FUNCT
    def write_counter(self, attr):
        data=attr.get_write_value()
        counter = AttrHelper.getDictValue(self.__Counter,data)
        _MerlinCamera.setEnableCounters(counter)
        
    @Core.DEB_MEMBER_FUNCT
    def read_depth(self, attr):
        depth = _MerlinCamera.getCounterDepth()
        attr.set_value(AttrHelper.getDictKey(self.__Depth,depth))
        
    @Core.DEB_MEMBER_FUNCT
    def write_depth(self, attr):
        data=attr.get_write_value()
        depth = AttrHelper.getDictValue(self.__Depth,data)
        _MerlinCamera.setCounterDepth(depth)

    @Core.DEB_MEMBER_FUNCT
    def read_gain(self, attr):
        gain = _MerlinCamera.getGain()
        attr.set_value(AttrHelper.getDictKey(self.__GainSetting,gain))
        
    @Core.DEB_MEMBER_FUNCT
    def write_gain(self, attr):
        data=attr.get_write_value()
        gain = AttrHelper.getDictValue(self.__GainSetting,data)
        _MerlinCamera.setGain(gain)
        
    @Core.DEB_MEMBER_FUNCT
    def read_operatingEnergy(self, attr):
        attr.set_value(_MerlinCamera.getOperatingEnergy())
        
    @Core.DEB_MEMBER_FUNCT
    def write_operatingEnergy(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setOperatingEnergy(data)
        
    @Core.DEB_MEMBER_FUNCT
    def read_temperature(self, attr):
        attr.set_value(_MerlinCamera.getTemperature())
                
    @Core.DEB_MEMBER_FUNCT
    def read_threshold0(self, attr):
        attr.set_value(_MerlinCamera.getThreshold(MerlinAcq.Camera.THRESHOLD0))
        
    @Core.DEB_MEMBER_FUNCT
    def write_threshold0(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setThreshold(MerlinAcq.Camera.THRESHOLD0, data);
        
    @Core.DEB_MEMBER_FUNCT
    def read_threshold1(self, attr):
        attr.set_value(_MerlinCamera.getThreshold(MerlinAcq.Camera.THRESHOLD1))
        
    @Core.DEB_MEMBER_FUNCT
    def write_threshold1(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setThreshold(MerlinAcq.Camera.THRESHOLD1, data);
        
    @Core.DEB_MEMBER_FUNCT
    def read_threshold2(self, attr):
        attr.set_value(_MerlinCamera.getThreshold(MerlinAcq.Camera.THRESHOLD2))
        
    @Core.DEB_MEMBER_FUNCT
    def write_threshold2(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setThreshold(MerlinAcq.Camera.THRESHOLD2, data);
        
    @Core.DEB_MEMBER_FUNCT
    def read_threshold3(self, attr):
        attr.set_value(_MerlinCamera.getThreshold(MerlinAcq.Camera.THRESHOLD3))
        
    @Core.DEB_MEMBER_FUNCT
    def write_threshold3(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setThreshold(MerlinAcq.Camera.THRESHOLD3, data);
        
    @Core.DEB_MEMBER_FUNCT
    def read_threshold4(self, attr):
        attr.set_value(_MerlinCamera.getThreshold(MerlinAcq.Camera.THRESHOLD4))
       
    @Core.DEB_MEMBER_FUNCT
    def write_threshold4(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setThreshold(MerlinAcq.Camera.THRESHOLD4, data);
        
    @Core.DEB_MEMBER_FUNCT
    def read_threshold5(self, attr):
        attr.set_value(_MerlinCamera.getThreshold(MerlinAcq.Camera.THRESHOLD5))
        
    @Core.DEB_MEMBER_FUNCT
    def write_threshold5(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setThreshold(MerlinAcq.Camera.THRESHOLD5, data);
        
    @Core.DEB_MEMBER_FUNCT
    def read_threshold6(self, attr):
        attr.set_value(_MerlinCamera.getThreshold(MerlinAcq.Camera.THRESHOLD6))
        
    @Core.DEB_MEMBER_FUNCT
    def write_threshold6(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setThreshold(MerlinAcq.Camera.THRESHOLD6, data);
        
    @Core.DEB_MEMBER_FUNCT
    def read_threshold7(self, attr):
        attr.set_value(_MerlinCamera.getThreshold(MerlinAcq.Camera.THRESHOLD7))
        
    @Core.DEB_MEMBER_FUNCT
    def write_threshold7(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setThreshold(MerlinAcq.Camera.THRESHOLD7, data);
         
    @Core.DEB_MEMBER_FUNCT
    def read_triggerStartType(self, attr):
        trig = _MerlinCamera.getTriggerStartType()
        attr.set_value(AttrHelper.getDictKey(self.__Trigger,trig))
        
    @Core.DEB_MEMBER_FUNCT
    def write_triggerStartType(self, attr):
        data=attr.get_write_value()
        trig = AttrHelper.getDictValue(self.__Trigger,data)
        _MerlinCamera.setTriggerStartType(trig)
        
    @Core.DEB_MEMBER_FUNCT
    def read_triggerStopType(self, attr):
        trig = _MerlinCamera.getTriggerStopType()
        attr.set_value(AttrHelper.getDictKey(self.__Trigger,trig))
        
    @Core.DEB_MEMBER_FUNCT
    def write_triggerStopType(self, attr):
        data=attr.get_write_value()
        trig = AttrHelper.getDictValue(self.__Trigger,data)
        _MerlinCamera.setTriggerStopType(trig)
        
    @Core.DEB_MEMBER_FUNCT
    def read_triggerOutTTL(self, attr):
        trigout = _MerlinCamera.getTriggerOutTTL()
        attr.set_value(AttrHelper.getDictKey(self.__TriggerOutput,trigout))
        
    @Core.DEB_MEMBER_FUNCT
    def write_triggerOutTTL(self, attr):
        data=attr.get_write_value()
        trigout = AttrHelper.getDictValue(self.__TriggerOutput,data)
        _MerlinCamera.setTriggerOutTTL(trigout)
        
    @Core.DEB_MEMBER_FUNCT
    def read_triggerOutLVDS(self, attr):
        trigout = _MerlinCamera.getTriggerOutLVDS()
        attr.set_value(AttrHelper.getDictKey(self.__TriggerOutput,trigout))
        
    @Core.DEB_MEMBER_FUNCT
    def write_triggerOutLVDS(self, attr):
        data=attr.get_write_value()
        trigout = AttrHelper.getDictValue(self.__TriggerOutput,data)
        _MerlinCamera.setTriggerOutLVDS(trigout)
        
    @Core.DEB_MEMBER_FUNCT
    def read_triggerOutTTLInvert(self, attr):
        trigout = _MerlinCamera.getTriggerOutTTLInvert()
        attr.set_value(AttrHelper.getDictKey(self.__TriggerLevel,trigout))
        
    @Core.DEB_MEMBER_FUNCT
    def write_triggerOutTTLInvert(self, attr):
        data=attr.get_write_value()
        trigout = AttrHelper.getDictValue(self.__TriggerLevel,data)
        _MerlinCamera.setTriggerOutTTLInvert(trigout)
        
    @Core.DEB_MEMBER_FUNCT
    def read_triggerOutLVDSInvert(self, attr):
        trigout = _MerlinCamera.getTriggerOutLVDSInvert()
        attr.set_value(AttrHelper.getDictKey(self.__TriggerLevel,trigout))
        
    @Core.DEB_MEMBER_FUNCT
    def write_triggerOutLVDSInvert(self, attr):
        data=attr.get_write_value()
        trigout = AttrHelper.getDictValue(self.__TriggerLevel,data)
        _MerlinCamera.setTriggerOutLVDSInvert(trigout)
        
    @Core.DEB_MEMBER_FUNCT
    def read_triggerInTTLDelay(self, attr):
        attr.set_value(_MerlinCamera.getTriggerInTTLDelay())
        
    @Core.DEB_MEMBER_FUNCT
    def write_triggerInTTLDelay(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setTriggerInTTLDelay(data)
        
    @Core.DEB_MEMBER_FUNCT
    def read_triggerInLVDSDelay(self, attr):
        attr.set_value(_MerlinCamera.getTriggerInLVDSDelay())
        
    @Core.DEB_MEMBER_FUNCT
    def write_triggerInLVDSDelay(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setTriggerInLVDSDelay(data)
        
    @Core.DEB_MEMBER_FUNCT
    def read_triggerUseDelay(self, attr):
        mode = _MerlinCamera.getTriggerUseDelay()
        attr.set_value(AttrHelper.getDictKey(self.__Switch,mode))
        
    @Core.DEB_MEMBER_FUNCT
    def write_triggerUseDelay(self, attr):
        data=attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__Switch,data)
        _MerlinCamera.setTriggerUseDelay(mode)
        
    @Core.DEB_MEMBER_FUNCT
    def read_thScanNum(self, attr):
        attr.set_value(_MerlinCamera.getTHScanNum())
        
    @Core.DEB_MEMBER_FUNCT
    def write_thScanNum(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setTHScanNum(data)
        
    @Core.DEB_MEMBER_FUNCT
    def read_thStart(self, attr):
        attr.set_value(_MerlinCamera.getTHStart())       
        
    @Core.DEB_MEMBER_FUNCT
    def write_thStart(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setTHStart(data)        
        
    @Core.DEB_MEMBER_FUNCT
    def read_thStop(self, attr):
        attr.set_value(_MerlinCamera.getTHStop())        
        
    @Core.DEB_MEMBER_FUNCT
    def write_thStop(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setTHStop(data)        
        
    @Core.DEB_MEMBER_FUNCT
    def read_thStep(self, attr):
        attr.set_value(_MerlinCamera.getTHStep())        
        
    @Core.DEB_MEMBER_FUNCT
    def write_thStep(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setTHStep(data)

    @Core.DEB_MEMBER_FUNCT
    def read_fileDirectory(self, attr):
        attr.set_value(_MerlinCamera.getFileDirectory())        
        
    @Core.DEB_MEMBER_FUNCT
    def write_fileDirectory(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setFileDirectory(data)

    @Core.DEB_MEMBER_FUNCT
    def read_fileName(self, attr):
        attr.set_value(_MerlinCamera.getFileName())        
        
    @Core.DEB_MEMBER_FUNCT
    def write_fileName(self, attr):
        data=attr.get_write_value()
        _MerlinCamera.setFileName(data)

    @Core.DEB_MEMBER_FUNCT
    def read_fileEnable(self, attr):
        mode = _MerlinCamera.getFileEnable()
        attr.set_value(AttrHelper.getDictKey(self.__Switch,mode))
        
    @Core.DEB_MEMBER_FUNCT
    def write_fileEnable(self, attr):
        data=attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__Switch,data)
        _MerlinCamera.setFileEnable(mode)

    @Core.DEB_MEMBER_FUNCT
    def read_fillMode(self, attr):
        mode = _MerlinCamera.getFillMode()
        attr.set_value(AttrHelper.getDictKey(self.__FillMode,mode))
        
    @Core.DEB_MEMBER_FUNCT
    def write_fillMode(self, attr):
        data=attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__FillMode,data)
        _MerlinCamera.setFillMode(mode)

    def read_acqRunning(self, attr):
        attr.set_value(_MerlinCamera.isAcqRunning())

    #-----------------------------------------------------------------------------
    #    Merlin command methods
    #-----------------------------------------------------------------------------
    
    @Core.DEB_MEMBER_FUNCT
    def SoftTrigger(self):
        _MerlinCamera.softTrigger()
        
    @Core.DEB_MEMBER_FUNCT
    def Abort(self):
         _MerlinCamera.abort()
        
    @Core.DEB_MEMBER_FUNCT
    def THScan(self):
        _MerlinCamera.thscan()
        
    @Core.DEB_MEMBER_FUNCT
    def ResetHW(self):
        _MerlinCamera.resetHw()        

class MerlinClass(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {
        }


    #    Device Properties
    device_property_list = {
        'HostName':
            [PyTango.DevString,
            "The name of the Merlin PC",
            [] ],
        'CmdPort':
            [PyTango.DevLong,
            "The Merlin command port",
            [6341]],
        'DataPort':
            [PyTango.DevLong,
            "The Merlin data port",
            [6342]],
        'Chips':
            [PyTango.DevLong,
            "Nos of Medipix chips",
            [4]],
        'ImageWidth':
            [PyTango.DevLong,
            "The width of Merlin detector head in pixels",
            [512]],
        'ImageHeight':
            [PyTango.DevLong,
            "The height of the Merlin detector head in Pixels",
            [512]],
        'Simulate':
            [PyTango.DevBoolean,
            "Simulate the Merlin commands.",
            [False]],
        }


    #    Command definitions
    cmd_list = {
        'SoftTrigger':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        'Abort':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        'THScan':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        'ResetHW':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        }


    #    Attribute definitions
    attr_list = {
        'softwareVersion':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ]],
        'chargeSumming':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Charge Summming mode',
             'unit': 'ON/OFF',
                }],
        'colourMode':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Colour mode',
             'unit': 'MONOCHROME/COLOUR',
                }],
        'continuousRW':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Continuous Collection',
             'unit': 'ON/OFF',
                }],
        'counter':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Counter ',
             'unit': 'COUNTER0/COUNTER1/BOTH',
                }],
        'depth':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Counter depth ',
             'unit': 'BPP1/BPP6/BPP12/BPP24',
                }],
        'gain':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Gain Settings',
             'unit': 'SHGM/HGM/LGM/SLGM',
                }],
        'operatingEnergy':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Energy',
             'unit': 'keV',
             'min_value': '0',
             'max_value': '999.99',             
                }],
        'temperature':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ],
            {
             'label':'Temperature',
             'unit': 'degrees C',
                }],
        'threshold0':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Threshold 0',
             'unit': 'keV',
             'min_value': '0',
             'max_value': '999.99',             
                }],
        'threshold1':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Threshold 1',
             'unit': 'keV',
             'min_value': '0',
             'max_value': '999.99',             
                }],
        'threshold2':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Threshold 2',
             'unit': 'keV',
             'min_value': '0',
             'max_value': '999.99',             
                }],
        'threshold3':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Threshold 3',
             'unit': 'keV',
             'min_value': '0',
             'max_value': '999.99',             
                }],
        'threshold4':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Threshold 4',
             'unit': 'keV',
             'min_value': '0',
             'max_value': '999.99',             
                }],
        'threshold5':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Threshold 5',
             'unit': 'keV',
             'min_value': '0',
             'max_value': '999.99',             
                }],
        'threshold6':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Threshold 6',
             'unit': 'keV',
             'min_value': '0',
             'max_value': '999.99',             
                }],
        'threshold7':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Threshold 7',
             'unit': 'keV',
             'min_value': '0',
             'max_value': '999.99',             
                }],
        'triggerStartType':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Trigger start mode',
             'unit': 'INTERNAL/RISING_EDGE_TTL/FALLING_EDGE_TTL/RISING_EDGE_LVDS/FALLING_EDGE_LVDS/SOFT',
                }],
        'triggerStopType':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Trigger stop mode',
             'unit': 'INTERNAL/RISING_EDGE_TTL/FALLING_EDGE_TTL/RISING_EDGE_LVDS/FALLING_EDGE_LVDS/SOFT',
                }],
        'triggerInTTL':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'TTL Trigger stop mode',
             'unit': 'TTL/LVDS/TTL_DELAYED/LVDS_DELAYED/FOLLOW_SHUTTER/ONE_PER_ACQ_BURST/SHUTTER_AND_SENSOR_READ/OUTPUT_BUSY',
                }],
        'triggerInLVDS':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'LVDS Trigger stop mode',
             'unit': 'TTL/LVDS/TTL_DELAYED/LVDS_DELAYED/FOLLOW_SHUTTER/ONE_PER_ACQ_BURST/SHUTTER_AND_SENSOR_READ/OUTPUT_BUSY',
                }],
        'triggerOutTTLInvert':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'TTL Trigger invert mode',
             'unit': 'NORMAL/INVERTED',
                }],
        'triggerOutLVDSInvert':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'LVDS Trigger invert mode',
             'unit': 'NORMAL/INVERTED',
                }],
        'triggerInTTLDelay':
            [[PyTango.DevLong64,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'TTL Trigger delay',
             'unit': 'ns',
             'min_value': '0',
             'max_value': '68719476720',             
                }],
        'triggerInLVDSDelay':
            [[PyTango.DevLong64,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'LVDS Trigger delay',
             'unit': 'ns',
             'min_value': '0',
             'max_value': '68719476720',             
                }],
        'triggerUseDelay':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Use Trigger delay',
             'unit': 'ON/OFF',
                }],
        'thScanNum':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Threshold number to scan',
             'unit': '',
             'min_value': '0',
             'max_value': '7',             
                }],
        'thStart':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Threshold scan start energy',
             'unit': 'keV',
             'min_value': '0',
             'max_value': '999.99',             
                }],
        'thStop':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Threshold scan stop energy',
             'unit': 'keV',
             'min_value': '0',
             'max_value': '999.99',             
                }],
        'thStep':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Threshold scan increment energy',
             'unit': 'keV',
             'min_value': '0',
             'max_value': '999.99',             
                }],
         'fileDirectory':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Directory name if saving on Merlin PC',
                }],
         'fileName':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Filename if saving on Merlin PC',
                }],
        'fileEnable':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Enable file saving to Merlin PC',
             'unit': 'ON/OFF',
                }],

        'fillMode':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Set the Fillmode for inter-chip gap',
             'unit': 'NoFill/InsertZero/Distribute/Interpolate',
                }],

          'acqRunning':
            [[PyTango.DevBoolean,
              PyTango.SCALAR,
              PyTango.READ],
            {
             'label':'Acquisition active',
             'unit': '',
                }],
        }

    def __init__(self, name) :
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name)

#------------------------------------------------------------------
#------------------------------------------------------------------
# Plugins
#------------------------------------------------------------------
#------------------------------------------------------------------

_MerlinCamera = None
_MerlinInterface = None

def get_control(HostName="", CmdPort=6431, DataPort=6432, ImageWidth=512, ImageHeight=512, Chips=4, Simulate=False, **keys) :
    global _MerlinCamera
    global _MerlinInterface
#    Core.DebParams.setTypeFlags(Core.DebParams.AllFlags)
    if _MerlinInterface is None:
        print('Starting and configuring the Merlin camera ...')
        _MerlinCamera = MerlinAcq.Camera(HostName, int(CmdPort), int(DataPort), int(ImageWidth), int(ImageHeight), int(Chips), bool(Simulate))
        _MerlinInterface = MerlinAcq.Interface(_MerlinCamera)
        print('Merlin Camera (%s:%s) is started'%(_MerlinCamera.getDetectorType(),_MerlinCamera.getDetectorModel()))
    return Core.CtControl(_MerlinInterface)

def get_tango_specific_class_n_device():
    return MerlinClass, Merlin

