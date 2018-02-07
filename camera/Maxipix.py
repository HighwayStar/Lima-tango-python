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
#=============================================================================
#
# file :        Maxipix.py
#
# description : Python source for the Maxipix and its commands. 
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
from Lima import Maxipix as MaxipixModule
# import some useful helpers to create direct mapping between tango attributes
# and Lima APIs.
from Lima.Server import AttrHelper

class Maxipix(PyTango.Device_4Impl):

    Core.DEB_CLASS(Core.DebModApplication, 'Maxipix')
    

#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self,*args) :
        PyTango.Device_4Impl.__init__(self,*args)

        self.__SignalLevel = {'LOW_FALL': MaxipixModule.PriamAcq.LOW_FALL,\
                              'HIGH_RISE': MaxipixModule.PriamAcq.HIGH_RISE}
        self.__ReadyLevel = self.__SignalLevel
        self.__GateLevel = self.__SignalLevel
        self.__TriggerLevel = self.__SignalLevel
        self.__ShutterLevel = self.__SignalLevel
        
        self.__ReadyMode =   {'EXPOSURE': MaxipixModule.PriamAcq.EXPOSURE,\
                              'EXPOSURE_READOUT': MaxipixModule.PriamAcq.EXPOSURE_READOUT}
        self.__GateMode =    {'INACTIVE': MaxipixModule.PriamAcq.INACTIVE,\
                              'ACTIVE': MaxipixModule.PriamAcq.ACTIVE}
        self.__FillMode =    {'RAW': MaxipixModule.MaxipixReconstruction.RAW,
                              'ZERO': MaxipixModule.MaxipixReconstruction.ZERO,
                              'DISPATCH': MaxipixModule.MaxipixReconstruction.DISPATCH,
                              'MEAN': MaxipixModule.MaxipixReconstruction.MEAN
                              }
        
        self.__Attribute2FunctionBase = {'signal_level': 'SignalLevel',
                                         'ready_level': 'ReadyLevel',
                                         'gate_level': 'GateLevel',
                                         'shutter_level': 'ShutterLevel',
                                         'trigger_level': 'TriggerLevel',
                                         'ready_mode': 'ReadyMode',
                                         'gate_mode': 'GateMode',
                                         'fill_mode': 'FillMode',
                                         'energy_threshold': 'Energy'
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
        _PriamAcq = _MaxipixInterface.priamAcq()
        if prop_name.count('fill_mode'):
            func = getattr(_MaxipixInterface, 'set'+name)
        else:
            func = getattr(_PriamAcq, 'set'+name)
        deb.Always('Setting property '+prop_name) 

        val = AttrHelper.getDictValue(dict, key.upper())
        if  val is None:
            deb.Error('Wrong value for property %s :%s' % (prop_name, val))
        else:
            if extra is not None: func(extra,val)
            else: func(val)

    def __getConfigNameList(self):
        spath= os.path.normpath(self.config_path)
        if not os.path.isdir(spath):
            PyTango.Except.throw_exception('WrongData',\
                                           'Invalid path: %s'%(self.config_path),\
                                           'Maxipix Class') 

        else:
            dirList = os.listdir(spath)
            fileDict={}
            fileList=[]
            for file in dirList:
                if file.endswith('.cfg'):
                    filePath = spath+'/'+file
                    fileStat = os.stat(filePath)
                    modifiedTime = fileStat.st_mtime
                    fileDict[modifiedTime]= file.strip('.cfg')
        if fileDict:
            timeList = list(fileDict.keys());timeList.sort()
            for mTime in timeList:
                fileList.append(fileDict[mTime])
                #fileList.append(time.ctime(mTime))
        return fileList
                     
        
#==================================================================
#
#    Maxipix read/write attribute methods
#
#==================================================================

    def __getattr__(self,name) :
        _PriamAcq = _MaxipixInterface.priamAcq()
        if name.count('fill_mode') or name.count('energy_threshold'):
            return AttrHelper.get_attr_4u(self, name, _MaxipixInterface)
        else:
            return AttrHelper.get_attr_4u(self, name, _PriamAcq)
            
        
    ## @brief read the config name
    #
    def read_config_name(self,attr) :
        cfg_name = ""
        if self.config_name:
            cfg_name = self.config_name
        attr.set_value(cfg_name)

    ## @brief Write the config name and load it
    #
    def write_config_name(self,attr) :
        data = attr.get_write_value()
        _MaxipixInterface.loadConfig(data)
        self.config_name = data

    ## @brief read the config path
    #
    def read_config_path(self,attr) :
        cfg_path = ""
        if self.config_path:
            cfg_path = self.config_path
        attr.set_value(cfg_path)

    ## @brief Write the config path
    #
    def write_config_path(self,attr) :
        data = attr.get_write_value()
        _MaxipixInterface.setPath(data)
        self.config_path = data

    ## @brief read the board id
    #
    def read_espia_dev_nb(self,attr) :
        espia_dev_nb = 0
        if self.espia_dev_nb:
            espia_dev_nb = self.espia_dev_nb
        attr.set_value(espia_dev_nb)


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
        if attr_name.count('config_name'):
            return self.__getConfigNameList()
        else:
            return AttrHelper.get_attr_string_value_list(self, attr_name)

class MaxipixClass(PyTango.DeviceClass):

    class_property_list = {}

    device_property_list = {
        'espia_dev_nb':
        [PyTango.DevShort,
         "Espia board device number",[]],
        'config_path':
        [PyTango.DevString,
         "Path where configuration files are",[]],
        'config_name':
        [PyTango.DevString,
         "The default configuration loaded",[]],
        'reconstruction_active':
        [PyTango.DevBoolean,
         "Set active or inactive the image reconstruction",[]],
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
        }

    attr_list = {
        'energy_threshold':
        [[PyTango.DevDouble,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':"Energy threshold",
             'unit':"KeV",
             'format':"%5.2f",
             'description':"Energy threshold (KeV)",
         }],
        'config_name':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label':"Configuration name",
             'unit':"N/A",
             'format':"",
             'description':"root name of the configuration files",
         }],
        'config_path':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
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
        'espia_dev_nb':	  
        [[PyTango.DevShort,
          PyTango.SCALAR,
          PyTango.READ],
         {
             'label':"Espia board number",
             'unit':"number",
             'format':"",
             'description':"The Espia board device number",
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

_MaxipixCamera = None
_MaxipixInterface = None

def get_control(espia_dev_nb = '0',config_path='', config_name='', reconstruction_active='true', **keys) :
    #properties are passed here as string
    global _MaxipixCamera
    global _MaxipixInterface

    if reconstruction_active.lower() == 'true': active = True
    else: active  = False
    if _MaxipixCamera is None:
        _MaxipixCamera = MaxipixModule.Camera(int(espia_dev_nb), config_path, config_name, active)
        _MaxipixInterface = MaxipixModule.Interface(_MaxipixCamera)
        
    return Core.CtControl(_MaxipixInterface)

    
def get_tango_specific_class_n_device():
    return MaxipixClass,Maxipix
