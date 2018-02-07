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
# file :        MetaMaxipix2.py
#
# description : Python source for the MetaMaxipix2, a Lima Meta detector
#                for 2x1 or 1x2 maxipix meta assembly. 
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
from Lima.Maxipix.MpxCommon import MpxError
from Lima import Meta

# import some useful helpers to create direct mapping between tango attributes
# and Lima interfaces.
from Lima.Server import AttrHelper


class MetaMaxipix:
    Core.DEB_CLASS(Core.DebModApplication, 'MetaMaxipix2')

    @Core.DEB_MEMBER_FUNCT
    def __init__(self, mpx1, mpx2):
        self.mpx1 = mpx1; self.mpx2=mpx2
        self.priam1 = mpx1.getPriamAcq()
        self.priam2 = mpx2.getPriamAcq()
                
    @Core.DEB_MEMBER_FUNCT
    def setFillMode(self, mode):
        self.mpx1.setFillMode(mode)
        self.mpx2.setFillMode(mode)
                
    @Core.DEB_MEMBER_FUNCT
    def getFillMode(self):
        if self.mpx1.getFillMode() != self.mpx2.getFillMode():
            return -1
        else:
            return self.mpx1.getFillMode()

    
    @Core.DEB_MEMBER_FUNCT
    def setReadyMode(self, mode):
        self.priam1.setReadyMode(mode)
        self.priam2.setReadyMode(mode)
        
    @Core.DEB_MEMBER_FUNCT
    def getReadyMode(self):
        if self.priam1.getReadyMode() != self.priam2.getReadyMode():
            return -1
        else:
            return self.priam1.getReadyMode()
        
    @Core.DEB_MEMBER_FUNCT
    def setGateMode(self, mode):
        self.priam1.setGateMode(mode)
        self.priam2.setGateMode(mode)
        
    @Core.DEB_MEMBER_FUNCT
    def getGateMode(self):
        if self.priam1.getGateMode() != self.priam2.getGateMode():
            return -1
        else:
            return self.priam1.getGateMode()
        
    @Core.DEB_MEMBER_FUNCT
    def setReadyLevel(self, level):
        self.priam1.setReadyLevel(level)
        self.priam2.setReadyLevel(level)
        
    @Core.DEB_MEMBER_FUNCT
    def getReadyLevel(self):
        if self.priam1.getReadyLevel() != self.priam2.getReadyLevel():
            return -1
        else:
            return self.priam1.getReadyLevel()
        
    @Core.DEB_MEMBER_FUNCT
    def setGateLevel(self, level):
        self.priam1.setGateLevel(level)
        self.priam2.setGateLevel(level)
        
    @Core.DEB_MEMBER_FUNCT
    def getGateLevel(self):
        if self.priam1.getGateLevel() != self.priam2.getGateLevel():
            return -1
        else:
            return self.priam1.getGateLevel()

    @Core.DEB_MEMBER_FUNCT
    def setTriggerLevel(self, level):
        self.priam1.setTriggerLevel(level)
        self.priam2.setTriggerLevel(level)

    @Core.DEB_MEMBER_FUNCT
    def getTriggerLevel(self):
        if self.priam1.getTriggerLevel() != self.priam2.getTriggerLevel():
            return -1
        else:
            return self.priam1.getTriggerLevel()
    
    @Core.DEB_MEMBER_FUNCT
    def setShutterLevel(self, level):
        self.priam1.setShutterLevel(level)
        self.priam2.setShutterLevel(level)
        
    @Core.DEB_MEMBER_FUNCT
    def getShutterLevel(self):
        if self.priam1.getShutterLevel() != self.priam2.getShutterLevel():
            return -1
        else:
            return self.priam1.getTriggerLevel()
        
    @Core.DEB_MEMBER_FUNCT
    def setEnergyThreshold(self, thl):
        self.mpx1.mpxDacs.setEThl(thl)
        self.mpx2.mpxDacs.setEThl(thl)
        self.mpx1.mpxDacs.applyChipDacs(0)
        self.mpx2.mpxDacs.applyChipDacs(0)
        
        
    @Core.DEB_MEMBER_FUNCT
    def getEnergyThreshold(self):
        val1 = self.mpx1.mpxDacs.getEThl(); val2 = self.mpx2.mpxDacs.getEThl()
        if val1 is None: val1 = -1
        if val2 is None: val2 = -1
        return (val2+val2)/2
        
    def getConfigName(self,attr) :
        cfg_name = ""
        if self.config_name_m1 and self.config_name_m2:
            cfg_name = self.config_name_m1 + " - " + config_name_m2
        return cfg_name


    ## @brief read the config path
    #
    def getConfigPath(self,attr) :
        cfg_path = ""
        if self.config_path_m1:
            cfg_path = self.config_path_m1
        return cfg_path

        

class MetaMaxipix2(PyTango.Device_4Impl):

    Core.DEB_CLASS(Core.DebModApplication, 'MetaMaxipix2')
    

#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self,*args) :
        PyTango.Device_4Impl.__init__(self,*args)

        _PriamAcq = _MaxipixAcqM1.getPriamAcq()
        self.__SignalLevel = {'LOW_FALL': _PriamAcq.LOW_FALL,\
                              'HIGH_RISE': _PriamAcq.HIGH_RISE,
                              '??': -1}
        
        self.__ReadyLevel = self.__SignalLevel
        self.__GateLevel = self.__SignalLevel
        self.__TriggerLevel = self.__SignalLevel
        self.__ShutterLevel = self.__SignalLevel
        
        self.__ReadyMode =   {'EXPOSURE': _PriamAcq.EXPOSURE,\
                              'EXPOSURE_READOUT': _PriamAcq.EXPOSURE_READOUT}
        self.__GateMode =    {'INACTIVE': _PriamAcq.INACTIVE,\
                              'ACTIVE': _PriamAcq.ACTIVE}
        self.__FillMode =    _MaxipixAcqM1.mpxFillModes
        
        self.__dacname = "thl"
        
        self.__Attribute2FunctionBase = {'signal_level': 'SignalLevel',
                                         'ready_level': 'ReadyLevel',
                                         'gate_level': 'GateLevel',
                                         'shutter_level': 'ShutterLevel',
                                         'trigger_level': 'TriggerLevel',
                                         'ready_mode': 'ReadyMode',
                                         'gate_mode': 'GateMode',
                                         'fill_mode': 'FillMode',
                                         }

        self.__MetaMpx = MetaMaxipix(_MaxipixAcqM1, _MaxipixAcqM2)
        
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

        # Apply property to the attributes

        for attr_name in ['fill_mode','ready_mode','ready_level','gate_mode','gate_level','shutter_level','trigger_level'] :       
            self.applyNewPropery(attr_name ,None)
                                         
	
#==================================================================
# 
# Some Utils
#
#==================================================================

    @Core.DEB_MEMBER_FUNCT
    def applyNewPropery(self, prop_name, extra=None):
        if extra is not None: name = self.__OtherAttribute2FunctionBase[prop_name]
        else: name = self.__Attribute2FunctionBase[prop_name]
        key = getattr(self, prop_name)
        if not key: return # property is not set
        
        dict = getattr(self, '_'+self.__class__.__name__+'__'+name)
        func = getattr(self.__MetaMpx, 'set'+name)
        deb.Always('Setting property '+prop_name) 

        val = AttrHelper.getDictValue(dict, key.upper())
        if  val is None:
            deb.Error('Wrong value for property %s :%s' % (prop_name, val))
        else:
            if extra is not None: func(extra,val)
            else: func(val)

        
#==================================================================
#
#    Maxipix read/write attribute methods
#
#==================================================================

            
    def __getattr__(self,name) :
        return AttrHelper.get_attr_4u(self, name, self.__MetaMpx)


    @Core.DEB_MEMBER_FUNCT
    def read_config_path(self, attr):
        cfg_path = ''
        if self.config_path_m1 and self.config_path_m2:
            cfg_path = self.config_path_m1        
        attr.set_value(cfg_path)
        
    @Core.DEB_MEMBER_FUNCT
    def read_config_name(self, attr):
        cfg_name = ''
        if self.config_name_m1 and self.config_name_m2:
            cfg_name = 'm1:'+self.config_name_m1 +'/m2:'+self.config_name_m2
        attr.set_value(cfg_name)
        

#==================================================================
#
#    Maxipix command methods
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

#------------------------------------------------------------------
#    setDebugFlags command:
#
#    Description: Get the current acquired frame number
#    argout: DevVarDoubleArray    
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def setDebugFlags(self, deb_flags):
        deb_flags &= 0xffffffff
        deb.Param('Setting debug flags: 0x%08x' % deb_flags)
        Core.DebParams.setTypeFlags((deb_flags   >> 16)  & 0xff)
        Core.DebParams.setModuleFlags((deb_flags >>  0)  & 0xffff)

        deb.Trace('FormatFlags: %s' % Core.DebParams.getFormatFlagsNameList())
        deb.Trace('TypeFlags:   %s' % Core.DebParams.getTypeFlagsNameList())
        deb.Trace('ModuleFlags: %s' % Core.DebParams.getModuleFlagsNameList())

#------------------------------------------------------------------
#    getDebugFlags command:
#
#    Description: Get the current acquired frame number
#    argout: DevVarDoubleArray    
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def getDebugFlags(self):
        deb.Trace('FormatFlags: %s' % Core.DebParams.getFormatFlagsNameList())
        deb.Trace('TypeFlags:   %s' % Core.DebParams.getTypeFlagsNameList())
        deb.Trace('ModuleFlags: %s' % Core.DebParams.getModuleFlagsNameList())
        
        deb_flags = (((Core.DebParams.getTypeFlags()    & 0xff)   << 16) |
                     ((Core.DebParams.getModuleFlags()  & 0xffff) <<  0))
        deb_flags &= 0xffffffff
        deb.Return('Getting debug flags: 0x%08x' % deb_flags)
        return deb_flags

class MetaMaxipix2Class(PyTango.DeviceClass):

    class_property_list = {}

    device_property_list = {
        'espia_dev_nb_m1':
        [PyTango.DevShort,
         "Espia board device number for detector module #1",[]],
        'espia_dev_nb_m2':
        [PyTango.DevShort,
         "Espia board device number for detector module #2",[]],
        'config_path_m1':
        [PyTango.DevString,
         "Configuration file path for module #1",[]],
        'config_path_m2':
        [PyTango.DevString,
         "Configuration file path for module #2",[]],
        'config_name_m1':
        [PyTango.DevString,
         "Configuration name for module #1",[]],
        'config_name_m2':
        [PyTango.DevString,
         "Configuration name for module #2",[]],
        'reconstruction_active':
        [PyTango.DevBoolean,
         "Set active or inactive the image reconstruction",[]],
        'meta_config':
        [PyTango.DevString,
         "Meta configuration: 2x1 or 1x2",['2x1']],
        'fill_mode':
        [PyTango.DevString,
         "The default configuration loaded",[]],	 
       'ready_level':
        [PyTango.DevString,
         "The ready output signal level",[]],	  
       'gate_level':
        [PyTango.DevString,
         "The gate output signal level",[]],	  
       'shutter_level':
        [PyTango.DevString,
         "The shutter output signal level",[]],	  
       'trigger_level':
        [PyTango.DevString,
         "The trigger output signal level",[]],	  
       'ready_mode':
        [PyTango.DevString,
         "The ready output signal level",[]],	  
       'gate_mode':
        [PyTango.DevString,
         "The gate output signal level",[]],	  
        }

    cmd_list = {
        'getAttrStringValueList':
        [[PyTango.DevString, "Attribute name"],
         [PyTango.DevVarStringArray, "Authorized String value list"]],
        'getDebugFlags':
        [[PyTango.DevVoid, ""],
         [PyTango.DevULong, "Debug flag in HEX format"]],
        'setDebugFlags':
        [[PyTango.DevULong, "Debug flag in HEX format"],
         [PyTango.DevVoid, ""]],
        }

    attr_list = {
        'energy_threshold':
        [[PyTango.DevDouble,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':"Energy thresholds",
             'unit':"keV",
             'format':"%5.2f",
             'description':"Threshold in energy (keV)",
         }],
        'config_name':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ],
         {
             'label':"Configuration name",
             'unit':"N/A",
             'format':"",
             'description':"root name of the configuration files",
         }],
        'config_path':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ],
         {
             'label':"Configuration directory path",
             'unit':"N/A",
             'format':"",
             'description':"Path of the configuration directory",
         }],
        'fill_mode':	  
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':"Fill mode",
             'unit':"enum.",
             'format':"",
             'description':"Between chip filling mode",
         }],	  
        'ready_mode':	  
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':"Ready output mode",
             'unit':"enum.",
             'format':"",
             'description':"Mode of the Ready output",
         }],	  
        'ready_level':	  
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':"Ready output level",
             'unit':"enum.",
             'format':"",
             'description':"The level logic of the Ready output",
         }],	  
        'shutter_level':	  
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':"Shutter output level",
             'unit':"enum.",
             'format':"",
             'description':"The level logic of the  Shutter output",
         }],	  
        'gate_mode':	  
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':"The Gate input mode",
             'unit':"enum.",
             'format':"",
             'description':"",
         }],	  
        'gate_level':	  
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':"",
             'unit':"",
             'format':"",
             'description':"",
         }],	  
        'trigger_level':	  
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':"",
             'unit':"",
             'format':"",
             'description':"",
         }],	  
        }


    def __init__(self,name) :
        PyTango.DeviceClass.__init__(self,name)
        self.set_type(name)


#----------------------------------------------------------------------------
#                              Plugins
#----------------------------------------------------------------------------
from Lima.Maxipix.MpxAcq import MpxAcq

_MaxipixAcqM1 = None
_MaxipixAcqM2 = None

def get_control(espia_dev_nb_m1 = '0', espia_dev_nb_m2='0',
                meta_config = '2x1',
                config_path_m1='', config_path_m2='',
                config_name_m1='', config_name_m2='',
                reconstruction_active='true', **keys) :
    #properties are passed here as string
    global _MaxipixAcqM1
    global _MaxipixAcqM2
    global _MaxipixInterfaceM1
    global _MaxipixInterfaceM2
    global _MetaInterface

    if reconstruction_active.lower() == 'true': active = True
    else: active  = False
    if _MaxipixAcqM1 is None and  _MaxipixAcqM2 is None: 
        _MaxipixAcqM1 = MpxAcq(int(espia_dev_nb_m1), config_path_m1, config_name_m1, active)
        _MaxipixAcqM2 = MpxAcq(int(espia_dev_nb_m2), config_path_m2, config_name_m2, active)
        
        _MaxipixInterfaceM1 = _MaxipixAcqM1.getInterface()
        _MaxipixInterfaceM2 = _MaxipixAcqM2.getInterface()
        _MetaInterface = Meta.Interface()
        if meta_config == '2x1':
            _MetaInterface.addInterface(0,0, _MaxipixInterfaceM1)
            _MetaInterface.addInterface(1,0, _MaxipixInterfaceM2)
            
        elif meta_config == '1x2':
            _MetaInterface.addInterface(0,0, _MaxipixInterfaceM1)
            _MetaInterface.addInterface(0,1, _MaxipixInterfaceM2)
        else:
            raise Exception("Invalid value for property meta_config: "+meta_config)

    return Core.CtControl(_MetaInterface)

    
def get_tango_specific_class_n_device():
    return MetaMaxipix2Class,MetaMaxipix2
