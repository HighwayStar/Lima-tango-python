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
## File :        Mythen3.py
## 
## Project :     Mythen3: A Dectris Mythen Detector System
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
import numpy
import sys
from Lima import Core
from Lima import Mythen3 as Mythen3Acq
from Lima.Server import AttrHelper

class Mythen3 (PyTango.Device_4Impl):

    Core.DEB_CLASS(Core.DebModApplication, 'LimaCCDs')
    
    def __init__(self, cl, name):
        PyTango.Device_4Impl.__init__(self, cl, name)
        Mythen3.init_device(self)

        self.__Status = {'Running' : Mythen3Acq.Camera.Running,
                         'WaitForTrigger' : Mythen3Acq.Camera.WaitForTrigger,
                         'NoDataInBuffer' : Mythen3Acq.Camera.NoDataInBuffer}

        self.__Switch = {'OFF': Mythen3Acq.Camera.OFF,
                         'ON': Mythen3Acq.Camera.ON}

        self.__Polarity = {'RISING_EDGE': Mythen3Acq.Camera.RISING_EDGE,
                           'FALLING_EDGE': Mythen3Acq.Camera.FALLING_EDGE}

        self.__Nbits = {'BPP4': Mythen3Acq.Camera.BPP4,
                        'BPP8': Mythen3Acq.Camera.BPP8,
                        'BPP16': Mythen3Acq.Camera.BPP16,
                        'BPP24': Mythen3Acq.Camera.BPP24}
        
        self.__Settings = {'Cu': Mythen3Acq.Camera.Cu,
                           'Mo': Mythen3Acq.Camera.Mo,
                           'Cr': Mythen3Acq.Camera.Cr,
                           'Ag': Mythen3Acq.Camera.Ag}


        self.init_device()

        
    def delete_device(self):
        pass

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.set_state(PyTango.DevState.ON)
        self.nbModules = _Mythen3Camera.getNbModules()
        self.module = 65535;
        self.setting = Mythen3Acq.Camera.Cu
        self.set_wattribute("badChannelInterpolation", "ON")
        self.set_wattribute("continuousTrigger", "OFF")
        self.set_wattribute("delayBeforeFrame", 0)
        self.set_wattribute("flatFieldCorrection", "ON")
        self.set_wattribute("gateMode", "OFF")
        self.set_wattribute("gates", 1)
        self.set_wattribute("inputSignalPolarity", "RISING_EDGE")
        self.set_wattribute("module", self.module)
        self.set_wattribute("nbits", "BPP24")
        self.set_wattribute("nbModules", self.nbModules)
        self.set_wattribute("outputSignalPolarity", "RISING_EDGE")
        self.set_wattribute("predefinedSettings", "Cu")
        self.set_wattribute("rateCorrection", "OFF")
        self.set_wattribute("triggered", "OFF")
        self.set_wattribute("energy", [8.05])
        self.set_wattribute("kthresh", [6.4])
        self.set_wattribute("tau", [197.6159])
        self.set_wattribute("useRawReadout", "OFF")

    def set_wattribute(self, attr_name, value):
        attr = Mythen3.get_device_attr(self).get_attr_by_name(attr_name)
        attr.set_write_value(value)

    #-----------------------------------------------------------------------------
    #    Mythen3 read/write attribute methods
    #-----------------------------------------------------------------------------
    
    @Core.DEB_MEMBER_FUNCT
    def read_assemblyDate(self, attr):
        attr.set_value(_Mythen3Camera.getAssemblyDate())

    @Core.DEB_MEMBER_FUNCT
    def read_badChannels(self, attr):
        data = _Mythen3Camera.getBadChannels()
        __dataflat_cache = numpy.array(data.buffer)
        __dataflat_cache.dtype = numpy.int32
        data.releaseBuffer()
        attr.set_value(__dataflat_cache)

    @Core.DEB_MEMBER_FUNCT
    def read_commandID(self, attr):
        attr.set_value(_Mythen3Camera.getCommandId())

    @Core.DEB_MEMBER_FUNCT
    def read_serialNumbers(self, attr):
        data = _Mythen3Camera.getSerialNumbers(); 
        attr.set_value([data[i] for i in range(len(data))])

    @Core.DEB_MEMBER_FUNCT
    def read_maxNbModules(self, attr):
        attr.set_value(_Mythen3Camera.getMaxNbModules())

    @Core.DEB_MEMBER_FUNCT
    def read_sensorMaterial(self, attr):
        attr.set_value(_Mythen3Camera.getSensorMaterial())

    @Core.DEB_MEMBER_FUNCT
    def read_sensorThickness(self, attr):
        attr.set_value(_Mythen3Camera.getSensorThickness())

    @Core.DEB_MEMBER_FUNCT
    def read_systemNum(self, attr):
        attr.set_value(_Mythen3Camera.getSystemNum())

    @Core.DEB_MEMBER_FUNCT
    def read_version(self, attr):
        attr.set_value(_Mythen3Camera.getVersion())

    @Core.DEB_MEMBER_FUNCT
    def read_module(self, attr):
        attr.set_value(_Mythen3Camera.getModule())

    @Core.DEB_MEMBER_FUNCT
    def write_module(self, attr):
        data = attr.get_write_value()
        _Mythen3Camera.setModule(data)

    @Core.DEB_MEMBER_FUNCT
    def read_nbModules(self, attr):
        attr.set_value(_Mythen3Camera.getNbModules())

    @Core.DEB_MEMBER_FUNCT
    def write_nbModules(self, attr):
        data = attr.get_write_value()
        _Mythen3Camera.setNbModules(data)

    @Core.DEB_MEMBER_FUNCT
    def read_nbits(self, attr):
        nbits = _Mythen3Camera.getNbits()
        attr.set_value(AttrHelper.getDictKey(self.__Nbits, nbits))

    @Core.DEB_MEMBER_FUNCT
    def write_nbits(self, attr):
        data = attr.get_write_value()
        nbits = AttrHelper.getDictValue(self.__Nbits, data)
        _Mythen3Camera.setNbits(nbits)

    @Core.DEB_MEMBER_FUNCT
    def read_hwStatus(self, attr):
        status = _Mythen3Camera.getHwStatus()
        attr.set_value(AttrHelper.getDictKey(self.__Status, status))

    @Core.DEB_MEMBER_FUNCT
    def read_energy(self, attr):
        data = _Mythen3Camera.getEnergy()
        attr.set_value([data[i] for i in range(len(data))])
 
    @Core.DEB_MEMBER_FUNCT
    def write_energy(self, attr):
        data = attr.get_write_value()
        _Mythen3Camera.setEnergy(data[0])

    @Core.DEB_MEMBER_FUNCT
    def read_energyMax(self, attr):
        attr.set_value(_Mythen3Camera.getEnergyMax())

    @Core.DEB_MEMBER_FUNCT
    def read_energyMin(self, attr):
        attr.set_value(_Mythen3Camera.getEnergyMin())

    @Core.DEB_MEMBER_FUNCT
    def read_kthresh(self, attr):
        data = _Mythen3Camera.getKThresh()
        attr.set_value([data[i] for i in range(len(data))])

    @Core.DEB_MEMBER_FUNCT
    def write_kthresh(self, attr):
        data = attr.get_write_value()
        _Mythen3Camera.setKThresh(data[0])

    @Core.DEB_MEMBER_FUNCT
    def read_kthreshMax(self, attr):
        attr.set_value(_Mythen3Camera.getKThreshMax())

    @Core.DEB_MEMBER_FUNCT
    def read_kthreshMin(self, attr):
        attr.set_value(_Mythen3Camera.getKThreshMin())

    @Core.DEB_MEMBER_FUNCT
    def write_kthreshEnergy(self, attr):
        data = attr.get_write_value()
        _Mythen3Camera.setKThreshEnergy(data[0], data[1])

    @Core.DEB_MEMBER_FUNCT
    def write_predefinedSettings(self, attr):
        data = attr.get_write_value()
        setting = AttrHelper.getDictCaseValue(self.__Settings, data)
        _Mythen3Camera.setPredefinedSettings(setting)

    @Core.DEB_MEMBER_FUNCT
    def read_badChannelInterpolation(self, attr):
        mode = _Mythen3Camera.getBadChannelInterpolation()
        attr.set_value(AttrHelper.getDictKey(self.__Switch, mode))

    @Core.DEB_MEMBER_FUNCT
    def write_badChannelInterpolation(self, attr):
        data = attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__Switch, data)
        _Mythen3Camera.setBadChannelInterpolation(mode)

    @Core.DEB_MEMBER_FUNCT
    def read_flatFieldCorrection(self, attr):
        mode = _Mythen3Camera.getFlatFieldCorrection()
        attr.set_value(AttrHelper.getDictKey(self.__Switch, mode))

    @Core.DEB_MEMBER_FUNCT
    def write_flatFieldCorrection(self, attr):
        data = attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__Switch, data)
        _Mythen3Camera.setFlatFieldCorrection(mode)

    @Core.DEB_MEMBER_FUNCT
    def read_cutoff(self, attr):
        attr.set_value(_Mythen3Camera.getCutoff())

    @Core.DEB_MEMBER_FUNCT
    def read_flatField(self, attr):
        data = _Mythen3Camera.getFlatField()
        __dataflat_cache = numpy.array(data.buffer)
        __dataflat_cache.dtype = numpy.int32
        data.releaseBuffer()
        attr.set_value(__dataflat_cache)

    @Core.DEB_MEMBER_FUNCT
    def read_rateCorrection(self, attr):
        mode = _Mythen3Camera.getRateCorrection()
        attr.set_value(AttrHelper.getDictKey(self.__Switch, mode))


    @Core.DEB_MEMBER_FUNCT
    def write_rateCorrection(self, attr):
        data = attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__Switch, data)
        _Mythen3Camera.setRateCorrection(mode)

    @Core.DEB_MEMBER_FUNCT
    def read_tau(self, attr):
        data = _Mythen3Camera.getTau()
        attr.set_value([data[i] for i in range(len(data))])

    @Core.DEB_MEMBER_FUNCT
    def write_tau(self, attr):
        data = attr.get_write_value()
        _Mythen3Camera.setTau(data[0])

    @Core.DEB_MEMBER_FUNCT
    def read_gates(self, attr):
        attr.set_value(_Mythen3Camera.getGates())

    @Core.DEB_MEMBER_FUNCT
    def write_gates(self, attr):
        data = attr.get_write_value()
        _Mythen3Camera.setGates(data)

    @Core.DEB_MEMBER_FUNCT
    def read_delayBeforeFrame(self, attr):
        attr.set_value(_Mythen3Camera.getDelayBeforeFrame())

    @Core.DEB_MEMBER_FUNCT
    def write_delayBeforeFrame(self, attr):
        data = attr.get_write_value()
        _Mythen3Camera.setDelayBeforeFrame(data)

    @Core.DEB_MEMBER_FUNCT
    def read_continuousTrigger(self, attr):
        mode = _Mythen3Camera.getContinuousTrigger()
        attr.set_value(AttrHelper.getDictKey(self.__Switch, mode))

    @Core.DEB_MEMBER_FUNCT
    def write_continuousTrigger(self, attr):
        data = attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__Switch, data)
        _Mythen3Camera.setContinuousTrigger(mode)

    @Core.DEB_MEMBER_FUNCT
    def read_gateMode(self, attr):
        mode = _Mythen3Camera.getGateMode()
        attr.set_value(AttrHelper.getDictKey(self.__Switch, mode))

    @Core.DEB_MEMBER_FUNCT
    def write_gateMode(self, attr):
        data = attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__Switch, data)
        _Mythen3Camera.setGateMode(mode)

    @Core.DEB_MEMBER_FUNCT
    def read_triggered(self, attr):
        mode = _Mythen3Camera.getTriggered()
        attr.set_value(AttrHelper.getDictKey(self.__Switch, mode))

    @Core.DEB_MEMBER_FUNCT
    def write_triggered(self, attr):
        data = attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__Switch, data)
        _Mythen3Camera.setTriggered(mode)


    @Core.DEB_MEMBER_FUNCT
    def read_inputSignalPolarity(self, attr):
        mode = _Mythen3Camera.getInputSignalPolarity()
        attr.set_value(AttrHelper.getDictKey(self.__Polarity, mode))

    @Core.DEB_MEMBER_FUNCT
    def write_inputSignalPolarity(self, attr):
        data = attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__Polarity, data)
        _Mythen3Camera.setInputSignalPolarity(mode)

    @Core.DEB_MEMBER_FUNCT
    def read_outputSignalPolarity(self, attr):
        mode = _Mythen3Camera.getOutputSignalPolarity()
        attr.set_value(AttrHelper.getDictKey(self.__Polarity, mode))

    @Core.DEB_MEMBER_FUNCT
    def write_outputSignalPolarity(self, attr):
        data = attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__Polarity, data)
        _Mythen3Camera.setOutputSignalPolarity(mode)

    @Core.DEB_MEMBER_FUNCT
    def read_testPattern(self, attr):
        data = _Mythen3Camera.getTestPattern()
        __dataflat_cache = numpy.array(data.buffer)
        __dataflat_cache.dtype = numpy.uint32
        data.releaseBuffer()
        attr.set_value(__dataflat_cache)

    def read_acqRunning(self, attr):
        attr.set_value(_Mythen3Camera.isAcqRunning())

    @Core.DEB_MEMBER_FUNCT
    def read_useRawReadout(self, attr):
        mode = _Mythen3Camera.getUseRawReadout()
        attr.set_value(AttrHelper.getDictKey(self.__Switch, mode))

    @Core.DEB_MEMBER_FUNCT
    def write_useRawReadout(self, attr):
        data = attr.get_write_value()
        mode = AttrHelper.getDictValue(self.__Switch, data)
        _Mythen3Camera.setUseRawReadout(mode)

#-----------------------------------------------------------------------------
    #    Mythen3 command methods
    #-----------------------------------------------------------------------------
    
    @Core.DEB_MEMBER_FUNCT
    def LogStart(self):
         _Mythen3Camera.logStart()
              
    @Core.DEB_MEMBER_FUNCT
    def LogStop(self):
       return _Mythen3Camera.logStop()

    @Core.DEB_MEMBER_FUNCT
    def LogRead(self):
       return _Mythen3Camera.logRead()

    @Core.DEB_MEMBER_FUNCT
    def ResetMythen(self):
        _Mythen3Camera.resetMythen()        
        self.init_device()

    @Core.DEB_MEMBER_FUNCT
    def ReadFrame(self, argin):
        data = _Mythen3Camera.readFrame(argin)
        __dataflat_cache = numpy.array(data.buffer)
        __dataflat_cache.dtype = numpy.uint32
        data.releaseBuffer()
        return __dataflat_cache

    @Core.DEB_MEMBER_FUNCT
    def ReadData(self):
        data = _Mythen3Camera.readData()
        __dataflat_cache = numpy.array(data.buffer.ravel())
        __dataflat_cache.dtype = numpy.uint32
        data.releaseBuffer()
        return __dataflat_cache

class Mythen3Class(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {
        }


    #    Device Properties
    device_property_list = {
        'HostName':
            [PyTango.DevString,
            "The name of the Mythen3 PC",
            [] ],
        'TcpPort':
            [PyTango.DevLong,
            "The Mythen3 command tcp port",
            [6341]],
        'Simulate':
            [PyTango.DevBoolean,
            "Simulate the Mythen3 commands.",
            [False]],
        }


    #    Command definitions
    cmd_list = {
        'LogStop':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        'LogStart':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        'LogRead':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        'ResetMythen':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        'ReadFrame':
            [[PyTango.DevLong, "frame number"],
            [PyTango.DevVarULongArray, "a frame of mythen data"]],
        'ReadData':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVarULongArray, "all frames of mythen data"]],
        }


    #    Attribute definitions
    attr_list = {
        'assemblyDate':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ],
            {
             'label':'Assembly date of the Mythen system',
                }],
        'badChannels':
            [[PyTango.DevLong,
            PyTango.SPECTRUM,
            PyTango.READ, 1280 * 24],
            {
             'label':'Display state of each channel',
                }],
        'commandID':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ],
            {
             'label':'Command identifier (increases by 1)',
                }],
        'serialNumbers':
            [[PyTango.DevLong,
            PyTango.SPECTRUM,
            PyTango.READ, 24],
            {
             'label':'Serial nos. of Mythen modules',
                }],
        'maxNbModules':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ],
            {
             'label':'Maximum nos. of Mythen modules',
                }],
        'sensorMaterial':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ],
            {
             'label':'The sensor material (0=silicon)',
                }],
        'sensorThickness':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ],
            {
             'label':'The sensor thickness',
             'unit': 'um',
                }],
        'systemNum':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ],
            {
             'label':'The serial number of the Mythen',
                }],
        'version':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ],
            {
             'label':'The software version of the socket server',
                }],
        'module':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Number of selected module (-1 = all)',
                }],
        'nbModules':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Number of modules in the system',
                }],
        'nbits':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Number of bits to readout',
             'unit': 'BPP24/BPP16/BPP8/BPP4',
                }],
        'hwStatus':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ]],
        'energy':
            [[PyTango.DevFloat,
            PyTango.SPECTRUM,
            PyTango.READ_WRITE, 24],
            {
             'label':'X-ray Energy',
             'unit': 'keV',
             'display_unit': 'keV',
	         'min_value': 4.09,
	         'max_value': 40.0,
                }],
        'energyMax':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ],
            {
             'label':'Maximum X-ray Energy',
             'unit': 'keV',
             'display_unit': 'keV',
                }],
        'energyMin':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ],
            {
             'label':'Minimum X-ray Energy',
             'unit': 'keV',
             'display_unit': 'keV',
                }],
        'kthresh':
            [[PyTango.DevFloat,
            PyTango.SPECTRUM,
            PyTango.READ_WRITE, 24],
            {
             'label':'Threshold Energy',
             'unit': 'keV',
             'display_unit': 'keV',
	         'min_value': 4.0,
	         'max_value': 20.0,
                }],
        'kthreshMax':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ],
            {
             'label':'Maximum Threshold Energy',
             'display_unit': 'keV',
             'unit': 'keV',
                }],
        'kthreshMin':
            [[PyTango.DevFloat,
            PyTango.SCALAR,
            PyTango.READ],
            {
             'label':'Minimum Threshold Energy',
             'display_unit': 'keV',
             'unit': 'keV',
                }],
        'kthreshEnergy':
            [[PyTango.DevFloat,
            PyTango.SPECTRUM,
            PyTango.WRITE, 2],
            {
             'label':'Threshold & Energy',
             'unit': 'keV',
             'display_unit': 'keV',
                }],
        'predefinedSettings':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.WRITE],
            {
             'label':'Load predefined energy/kthresh settings',
             'unit': 'Cu/Ag/Mo/Cr',
                }],
        'badChannelInterpolation':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Enable/Disable Bad Channel Interpolation Mode',
             'unit': 'ON/OFF',
                }],
        'flatFieldCorrection':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Enable/Disable Flat Field Correction Mode',
             'unit': 'ON/OFF',
                }],
        'cutoff':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ],
            {
             'label':'Count value before flatfield correction',
                }],
        'flatField':
            [[PyTango.DevLong,
            PyTango.SPECTRUM,
            PyTango.READ, 1280 * 24],
            {
             'label':'Flat field correction values',
                }],
        'rateCorrection':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Enable/Disable rate correction mode',
             'unit': 'ON/OFF',
                }],
        'tau':
            [[PyTango.DevFloat,
            PyTango.SPECTRUM,
            PyTango.READ_WRITE, 24],
            {
             'label':'Dead time constants for rate correction',
                }],
        'gates':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Number of gates per frame',
                }],
        'delayBeforeFrame':
            [[PyTango.DevLong64,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Time delay between trigger & start',
             'display_unit': '100ns',
             'unit': '100ns',
	         'min_value': 0,
                }],
        'continuousTrigger':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Enable/Disable continuous trigger mode',
             'unit': 'ON/OFF',
                }],
        'gateMode':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Enable/Disable gate mode',
             'unit': 'ON/OFF',
                }],
        'triggered':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Enable/Disable triggered mode',
             'unit': 'ON/OFF',
                }],
        'inputSignalPolarity':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Input Signal Polarity',
             'unit': 'RISING_EDGE/FALLING_EDGE',
                }],
        'outputSignalPolarity':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Output Signal Polarity',
             'unit': 'RISING_EDGE/FALLING_EDGE',
                }],
        'testPattern':
            [[PyTango.DevLong,
            PyTango.SPECTRUM,
            PyTango.READ, 1280 * 24],
            {
             'label':'Read back a test pattern',
                }],
        'acqRunning':
            [[PyTango.DevBoolean,
              PyTango.SCALAR,
              PyTango.READ],
            {
             'label':'Acquisition active',
             'unit': '',
                }],
        'useRawReadout':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
             'label':'Raw readout Mode (packed)',
             'unit': 'ON/OFF',
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

_Mythen3Camera = None
_Mythen3Interface = None

def get_control(HostName="160.103.146.190", TcpPort=1031, Simulate=False, **keys) :
    global _Mythen3Camera
    global _Mythen3Interface
#    Core.DebParams.setTypeFlags(Core.DebParams.AllFlags)
    if _Mythen3Interface is None:
        print('Starting and configuring the Mythen3 camera ...')
        _Mythen3Camera = Mythen3Acq.Camera(HostName, int(TcpPort), bool(int(Simulate)))
        _Mythen3Interface = Mythen3Acq.Interface(_Mythen3Camera)
        print('Mythen3 Camera (%s:%s) is started' % (_Mythen3Camera.getDetectorType(), _Mythen3Camera.getDetectorModel()))
    return Core.CtControl(_Mythen3Interface)

def get_tango_specific_class_n_device():
    return Mythen3Class, Mythen3

