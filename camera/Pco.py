############################################################################
# This file is part of LImA, a Library for Image Acquisition
#
# Copyright (C) : 2009-2011
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
# file :        Pco.py
#
# description : Python source for the Pco and its commands.
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
#=============================================================================
# 2016/06/02 - property params
#    split between 1 param (str) and more params (class 'PyTango._PyTango.StdStringVector')
#=============================================================================


import PyTango
import pdb
from Lima import Core
from Lima import Pco as PcoAcq
from Lima.Server import AttrHelper

VERSION_ATT ="20170707"

RESET_CLOSE_INTERFACE	= 100

class Pco(PyTango.Device_4Impl):

    Core.DEB_CLASS(Core.DebModApplication, 'LimaCCDs')

#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self,*args) :
        PyTango.Device_4Impl.__init__(self,*args)

        #self._Pco__Rollingshutter = { "only for EDGE": "-1", "GLOBAL": "0", "ROLLING":"1" }    

        self.__Attribute2FunctionBase = {
											'acqTimeoutRetry': 'AcqTimeoutRetry',
											'adc': 'Adc',
											'adcMax': 'AdcMax',
											'binInfo': 'BinningInfo',
											'bytesPerPixel': 'BytesPerPixel',
											'camInfo': 'CamInfo',
											'camName': 'CameraName',
											'camNameBase': 'CameraNameBase',
											'camNameEx': 'CameraNameEx',
											'camType': 'CamType',
											'cdiMode': 'CDIMode',
											'clXferPar': 'ClTransferParam',
											'cocRunTime': 'CocRunTime',
											'coolingTemperature': 'CoolingTemperature',
											'firmwareInfo': 'FirmwareInfo',
											'frameRate': 'FrameRate',
											'info': 'CamInfo',
											'lastError': 'LastError',
											'lastImgAcquired': 'LastImgAcquired',
											'lastImgRecorded': 'LastImgRecorded',
											'logMsg': 'MsgLog',
											'logPcoEnabled': 'PcoLogsEnabled',
											'maxNbImages': 'MaxNbImages',
											'pixelRate': 'PixelRate',
											'pixelRateInfo': 'PixelRateInfo',
											'pixelRateValidValues': 'PixelRateValidValues',
											'roiInfo': 'RoiInfo',
											'roiLastFixed': 'LastFixedRoi',
											'rollingShutter': 'RollingShutter',
											'rollingShutterInfo': 'RollingShutterInfo',
											'temperatureInfo': 'TemperatureInfo',
											'traceAcq': 'TraceAcq',
											'version': 'Version',
											'versionSdk': 'SdkRelease',
											'camerasFound': 'CamerasFound',
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
        self.get_device_properties(self.get_device_class())
        

#==================================================================
#
#    Pco read/write attribute methods
#
#==================================================================
    def __getattr__(self,name) :
        return AttrHelper.get_attr_4u(self, name, _PcoCam)

    def read_versionAtt(self,attr) :
        attr.set_value(VERSION_ATT)

#==================================================================
#
#    Pco command methods
#
#==================================================================
    @Core.DEB_MEMBER_FUNCT
    def getAttrStringValueList(self, attr_name):
        return AttrHelper.get_attr_string_value_list(self, attr_name)

    @Core.DEB_MEMBER_FUNCT
    def talk(self, argin):
        val= _PcoCam.talk(argin)
        return val

#==================================================================
#
#    PcoClass class definition
#
#==================================================================
class PcoClass(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {}

    #    Device Properties

    device_property_list = {
        'params':
        [PyTango.DevString,
           "general parameters",[]],
        'dummy':
        [PyTango.DevString,
           "dummy string",[]],
        'debug_control':
        [PyTango.DevString,
           "general debug",[]],
        'debug_module':
        [PyTango.DevString,
           "debug module flags",[]],
        'debug_format':
        [PyTango.DevString,
           "debug format flags",[]],
        'debug_type':
        [PyTango.DevString,
           "debug flags flags",[]]
        }


    #    Command definitions
    cmd_list = {
        'getAttrStringValueList':
        [[PyTango.DevString, "Attribute name"],
         [PyTango.DevVarStringArray, "Authorized String value list"]],
        'talk':
        [[PyTango.DevString, "str argin"],
         [PyTango.DevString, "str argout"]],
        }

    #    Attribute definitions
    attr_list = {
         'acqTimeoutRetry':	  
         [[PyTango.DevLong,
           PyTango.SCALAR,
           PyTango.READ_WRITE],
           {
             'unit': 'number',
             'format': '%d',
             'description': 'max Timeout retries during acq (0 - infinite)'
             }],

         'adc':	  
         [[PyTango.DevLong,
           PyTango.SCALAR,
           PyTango.READ_WRITE],
           {
             'unit': 'number',
             'format': '%d',
             'description': 'number of working ADC'
             }],

         'adcMax':	  
         [[PyTango.DevLong,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'number',
             'format': '%d',
             'description': 'max number of ADC'
             }],

         'binInfo':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'pco binning info'
             }],

         'bytesPerPixel':	  
         [[PyTango.DevLong,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'byte',
             'format': '%d',
             'description': 'bytes per pixel'
             }],

         'camInfo':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'general cam information'
             }],

         'camName':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'camera name'
             }],

         'camNameBase':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'camera name (pco)'
             }],

         'camNameEx':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'camera name, interface, sensor'
             }],

         'camType':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'camera type'
             }],

         'cdiMode':	  
         [[PyTango.DevLong,
           PyTango.SCALAR,
           PyTango.READ_WRITE], 
           {
    			"memorized":"true"
			}],

         'clXferPar':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'cameralink transfere parameters'
             }],

         'cocRunTime':	  
         [[PyTango.DevDouble,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 's',
             'format': '%g',
             'description': 'coc Runtime'
             }],


         'coolingTemperature':	  
         [[PyTango.DevLong,
           PyTango.SCALAR,
           PyTango.READ_WRITE], 
           {
             'unit': 'degrees',
             'format': '%d',
             'description': 'cooling temperature'
             }],

         'firmwareInfo':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'firmware info'
             }],

         'frameRate':	  
         [[PyTango.DevDouble,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'frames/s',
             'format': '%g',
             'description': 'frames per second (= 1/cocRuntime)'
             }],

         'info':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'general cam information'
             }],

         'lastError':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'last PCO error'
             }],

         'lastImgAcquired':	  
         [[PyTango.DevLong,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%ld',
             'description': 'last image acquired'
             }],

         'lastImgRecorded':	  
         [[PyTango.DevLong,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%ld',
             'description': 'last image recorded in camera RAM (not for all cams)'
             }],

         'logMsg':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'print the log msgs'
             }],

         'logPcoEnabled':	  
         [[PyTango.DevLong,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%d',
             'description': 'PCO logs are enabled'
           }],

         'maxNbImages':	  
         [[PyTango.DevLong,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%ld',
             'description': 'max nr of images in camera RAM (not for all cams)'
             }],

         'pixelRate':	  
         [[PyTango.DevLong,
           PyTango.SCALAR,
           PyTango.READ_WRITE],
           {
             'unit': 'Hz',
             'format': '%ld',
             'description': 'pixel rate in Hz'
           }],

         'pixelRateInfo':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'pixel rate info'
             }],

         'pixelRateValidValues':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'Hz',
             'format': '%s',
             'description': 'pixel rate valid values in Hz'
             }],

         'roiInfo':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'pco roi info'
             }],

         'roiLastFixed':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'last fixed roi info'
             }],

         'rollingShutter':	  
         [[PyTango.DevLong,
           PyTango.SCALAR,
           PyTango.READ_WRITE],
           {
             'unit': 'N/A',
             'format': '%d',
             'description': '1(Rolling), 2(Global), 4(Global Reset)'
           }],


         'rollingShutterInfo':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'rolling shutter info'
             }],

         'temperatureInfo':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'teperature info'
             }],

         'traceAcq':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'trace info during acq for some cameras'
             }],

         'version':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'complete version info'
             }],

         'versionAtt':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'att file version'
             }],

         'versionSdk':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'pco sdk release'
             }],

         'camerasFound':	  
         [[PyTango.DevString,
           PyTango.SCALAR,
           PyTango.READ],
           {
             'unit': 'N/A',
             'format': '%s',
             'description': 'cameras found during the Open search'
             }],

        }

#------------------------------------------------------------------
#    PcoClass Constructor
#------------------------------------------------------------------
    def __init__(self,name) :
        PyTango.DeviceClass.__init__(self,name)
        self.set_type(name)

#----------------------------------------------------------------------------
# Plugins
#----------------------------------------------------------------------------
_PcoCam = None
_PcoInterface = None
_PcoControl = None

def get_control(debug_control = "0", 
                debug_module = "0", 
                debug_type="0",
                mem_factor="0",
                debug_format = "0x31", 
                params = [], 
                **keys) :

    global _PcoCam
    global _PcoInterface
    global _PcoControl

    debControl = int(debug_control,0)
    debModule = int(debug_module,0)
    debType = int(debug_type,0)
    debFormat = int(debug_format,0)
    memFactor = int(mem_factor,0)

    if(type(params) == str):
		# <type 'str'>
        paramsIn = params
    else:
        # <class 'PyTango._PyTango.StdStringVector'>
        paramsIn = "".join("%s;" % (x,) for x in params)

    print("============= Properties =============")
    print("         keys:", keys)
    print("       params:", params)
    print("     paramsIn:", paramsIn)
    print("%s [%s] [0x%x]" % ("debug_control:", debug_control, debControl))
    print("%s [%s] [0x%x]" % (" debug_module:", debug_module, debModule))
    print("%s [%s] [0x%x]" % (" debug_format:", debug_format, debFormat))
    print("%s [%s] [0x%x]" % ("   debug_type:", debug_type, debType))
    print("%s [%s] [0x%x]" % ("   mem_factor:", mem_factor, memFactor))
    print("======================================")

    if debControl:
        Core.DebParams.setModuleFlags(debModule)
        Core.DebParams.setTypeFlags(debType)
    else:
        Core.DebParams.setTypeFlags(0)
        Core.DebParams.setModuleFlags(0)

    Core.DebParams.setFormatFlags(debFormat)


    if _PcoCam is None:
        _PcoCam = PcoAcq.Camera(paramsIn)
        _PcoInterface = PcoAcq.Interface(_PcoCam)
        _PcoControl = Core.CtControl(_PcoInterface)
        memFactor0 = _PcoControl.buffer().getMaxMemory()
        #_PcoControl.buffer().setMaxMemory(memFactor)
        #memFactor1 = _PcoControl.buffer().getMaxMemory()

    print("=================================================")
    #print "%s org[%d] req[%d] now[%d]" % ("   mem_factor:", memFactor0, memFactor, memFactor1)
    print("%s org[%d]" % ("   mem_factor:", memFactor0))
    print("=================================================")


    return _PcoControl


#----------------------------------------------------------------------------
#----------------------------------------------------------------------------
def get_tango_specific_class_n_device():
    return PcoClass,Pco


#==================================================================================
#==================================================================================
# called by ->  delete_device (LimaCCDs.py:352)   [LimaCCDs(id00/limaccds/pco2k1)]
# requiered to close properly the camera / sdk
#   because the cam, interface destructors are NOT called (?)
#==================================================================================
def close_interface():
    print("... close_interface()")
    _PcoInterface.reset(RESET_CLOSE_INTERFACE)

