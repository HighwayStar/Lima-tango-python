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

import itertools
import weakref
import PyTango
import sys
import numpy
import processlib
from Lima import Core
from .Utils import getDataFromFile,BasePostProcess

def grouper(n, iterable, padvalue=None):
    return zip(*[itertools.chain(iterable, itertools.repeat(padvalue, n-1))]*n)

RoiCounterTask = Core.Processlib.Tasks.RoiCounterTask

#==================================================================
#   RoiCounter Class Description:
#
#
#==================================================================


class RoiCounterDeviceServer(BasePostProcess) :

#--------- Add you global variables here --------------------------
    ROI_COUNTER_TASK_NAME = "RoiCounterTask"
#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self,cl, name):
        self.__roiCounterMgr = None
        self.__roiName2ID = {}
        self.__roiID2Name = {}
        self.__currentRoiId = 0
        BasePostProcess.__init__(self,cl,name)
        RoiCounterDeviceServer.init_device(self)
        try:
            ctControl = _control_ref()
            config = ctControl.config()

            class _RoiConfigSave(Core.CtConfig.ModuleTypeCallback) :
                def __init__(self,cnt):
                    Core.CtConfig.ModuleTypeCallback.__init__(self,"RoiCounters")
                    self.__cnt = weakref.ref(cnt)
                def store(self) :
                    cnt = self.__cnt()
                    return cnt.get_current_config()
                def restore(self,c) :
                    cnt = self.__cnt()
                    cnt.apply_config(c)

            self.__roiConfigsave = _RoiConfigSave(self)
            config.registerModule(self.__roiConfigsave)
        except AttributeError:
            pass

    def set_state(self,state) :
        if(state == PyTango.DevState.OFF) :
            if(self.__roiCounterMgr) :
                self.__roiCounterMgr = None
                ctControl = _control_ref()
                extOpt = ctControl.externalOperation()
                extOpt.delOp(self.ROI_COUNTER_TASK_NAME)
        elif(state == PyTango.DevState.ON) :
            if not self.__roiCounterMgr:
                ctControl = _control_ref()
                extOpt = ctControl.externalOperation()
                self.__roiCounterMgr = extOpt.addOp(Core.ROICOUNTERS,self.ROI_COUNTER_TASK_NAME,
                                                    self._runLevel)
            self.__roiCounterMgr.clearCounterStatus()

        PyTango.Device_4Impl.set_state(self,state)

#------------------------------------------------------------------
#    Read BufferSize attribute
#------------------------------------------------------------------
    def read_BufferSize(self, attr):
        value_read = self.__roiCounterMgr.getBufferSize()
        attr.set_value(value_read)


#------------------------------------------------------------------
#    Write BufferSize attribute
#------------------------------------------------------------------
    def write_BufferSize(self, attr):
        data = attr.get_write_value()
        self.__roiCounterMgr.setBufferSize(data)


#------------------------------------------------------------------
#    Read CounterStatus attribute
#------------------------------------------------------------------
    def read_CounterStatus(self, attr):
        value_read = self.__roiCounterMgr.getCounterStatus()
        attr.set_value(value_read)


#==================================================================
#
#    RoiCounter command methods
#
#==================================================================
    def addNames(self,argin):
        roi_id = []
        for roi_name in argin:
            if roi_name not in self.__roiName2ID:
                self.__roiName2ID[roi_name] = self.__currentRoiId
                self.__roiID2Name[self.__currentRoiId] = roi_name
                roi_id.append(self.__currentRoiId)
                self.__currentRoiId += 1
            else:
                roi_id.append(self.__roiName2ID[roi_name])
        return roi_id

    def removeRois(self,argin):
        if self.__roiCounterMgr :
            self.__roiCounterMgr.removeRois(argin)
        for roi_name in argin:
            roi_id = self.__roiName2ID.pop(roi_name,None)
            self.__roiID2Name.pop(roi_id,None)
        if not len(self.__roiName2ID):
            self.Stop()

    def setRois(self,argin) :
        if self.__roiCounterMgr is None:
            raise RuntimeError('should start the device first')

        if not len(argin) % 5:
            roi_list = []
            for roi_id,x,y,width,height in grouper(5,argin):
                roi_name = self.__roiID2Name.get(roi_id,None)
                if roi_name is None:
                    raise RuntimeError('should call add method before setRoi')
                roi_list.append((roi_name,Core.Roi(x,y,width,height)))
            self.__roiCounterMgr.updateRois(roi_list)
        else:
            raise AttributeError('should be a vector as follow [roi_id0,x0,y0,width0,height0,...')

    def setArcRois(self,argin) :
        if self.__roiCounterMgr is None:
            raise RuntimeError('should start the device first')

        if not len(argin) % 7:
            arc_list = []
            for roi_id,x,y,r1,r2,start,end in grouper(7,argin):
                roi_name = self.__roiID2Name.get(roi_id)
                if roi_name is None:
                    raise RuntimeError('should call add method before setRoi')
                arc_list.append((roi_name,Core.ArcRoi(x,y,r1,r2,start,end)))
            self.__roiCounterMgr.updateArcRois(arc_list)
        else:
            raise AttributeError('should be a vector as follow [roi_id,centerX,centerY,rayon1,rayon2,angle_start,angle_end,...]')

    def getNames(self):
        if self.__roiCounterMgr is None:
            raise RuntimeError('should start the device first')
        return self.__roiCounterMgr.getNames()       

    def getRoiTypes(self,argin):
        if self.__roiCounterMgr is None:
            raise RuntimeError('should start the device first')
        roi_type_list = []
        rois_types = self.__roiCounterMgr.getTypes()
        for roi_name in argin:
            for name, roi_type in rois_types:
                if name == roi_name:
                    break
            else:
                raise ValueError('Roi %s not defined yet' % roi_name)
            roi_type_map = {
                RoiCounterTask.SQUARE: 'SQUARE',
                RoiCounterTask.ARC:    'ARC',
                RoiCounterTask.MASK:   'MASK',
                RoiCounterTask.LUT:    'LUT',
            }
            roi_type_list.append(roi_type_map[roi_type])
        return roi_type_list

    def getRois(self,argin):
        if self.__roiCounterMgr is None:
            raise RuntimeError('should start the device first')
        roi_list = []
        rois_names =  self.__roiCounterMgr.getRois()
        for roi_name in argin:
            for name, roi in rois_names:
                if name == roi_name:
                    break
            else:
                raise ValueError('Roi %s not defined yet' % roi_name)
            roi_id = self.__roiName2ID[roi_name]
            x, y = roi.getTopLeft().x, roi.getTopLeft().y
            w, h = roi.getSize().getWidth(), roi.getSize().getHeight()
            roi_list.append((roi_id, x, y, w, h))
        roi_list_flat = list(itertools.chain(*roi_list))
        return numpy.array(roi_list_flat, numpy.uint32)

    def getArcRois(self,argin):
        if self.__roiCounterMgr is None:
            raise RuntimeError('should start the device first')
        roi_list = []
        rois_names =  self.__roiCounterMgr.getArcRois()
        for roi_name in argin:
            for name, roi in rois_names:
                if name == roi_name:
                    break
            else:
                raise ValueError('Roi %s not defined yet' % roi_name)
            roi_id = self.__roiName2ID[roi_name]
            x, y = roi.getCenter()
            r1, r2 = roi.getRayons()
            start, end = roi.getAngles()
            roi_list.append((roi_id, x, y, r1, r2, start, end))

        roi_list_flat = list(itertools.chain(*roi_list))
        return numpy.array(roi_list_flat, numpy.float64)

    def get_current_config(self):
        try:
            returnDict = {}
            if self.__roiCounterMgr:
                returnDict["active"] = True
                returnDict["runLevel"] = self._runLevel
                for name,roiTask in self.__roiCounterMgr.getTasks() :
                    rType = roiTask.getType()
                    if rType == roiTask.SQUARE:
                        x,y,width,height = roiTask.getRoi()
                        returnDict[name] = {"type":rType,"x":x,"y":y,
                                            "width":width,
                                            "height":height}
                    elif rType == roiTask.ARC:
                        x,y,r1,r2,a1,a2 = roiTask.getArcRoi()
                        returnDict[name] = {"type":rType,
                                            "x":x,"y":y,
                                            "r1":r1,"r2":r2,
                                            "a1":a1,"a2":a2}
                    else:
                        if rType == roiTask.LUT:
                            x,y,data = roiTask.getLut()
                        else:
                            x,y,data = roiTask.getLutMask()
                        returnDict[name] = {"type":rType,
                                            "x":x,"y":y,"data":data}
            else:
                returnDict["active"] = False
            return returnDict
        except:
            import traceback
            traceback.print_exc()

    def apply_config(self,c) :
        try:
            active = c.get("active",False)
            self.Stop()
            if active:
                self._runLevel = c.get("runLevel",0)
                self.Start()
                namedRois = []
                names = []
                for name,d in c.items() :
                    try:
                        if isinstance(d,dict):
                            rType = d.get("type",None)
                            if rType == RoiCounterTask.SQUARE:
                                x = d["x"]
                                y = d["y"]
                                width = d["width"]
                                height = d["height"]
                                namedRois.append((name,Core.Roi(x,y,width,height)))
                            elif rType == RoiCounterTask.ARC:
                                x = d["x"]
                                y = d["y"]
                                r1 = d["r1"]
                                r2 = d["r2"]
                                a1 = d["a1"]
                                a2 = d["a2"]
                                namedRois.append((name,Core.ArcRoi(x,y,r1,r2,a1,a2)))
                            elif rType == RoiCounterTask.MASK:
                                x = d["x"]
                                y = d["y"]
                                data = d["data"]
                                self.__roiCounterMgr.setLutMask(name,Core.Point(x,y),data)
                            elif rType == RoiCounterTask.LUT:
                                x = d["x"]
                                y = d["y"]
                                data = d["data"]
                                self.__roiCounterMgr.setLut(name,Core.Point(x,y),data)
                            names.append(name)
                    except KeyError as err:
                        PyTango.Except.throw_exception('Config error',
                                                       'Missing key %s in roi named %s'%(err,name),
                                                       'RoiCounterDeviceServer Class')
                self.__roiCounterMgr.updateRois(namedRois)
                self.add(names)
        except:
            import traceback
            traceback.print_exc()

    def clearAllRois(self):
        if self.__roiCounterMgr :
            self.__roiCounterMgr.clearAllRois()
            self.Stop()

    def setMaskFile(self,argin) :
        mask = getDataFromFile(*argin)
        self.__roiCounterMgr.setMask(mask)

    def readCounters(self,argin) :
        roiResultCounterList = self.__roiCounterMgr.readCounters(argin)
        if roiResultCounterList:
            minListSize = len(roiResultCounterList[0][1])
            for roiName,resultList in roiResultCounterList:
                if minListSize > len(resultList):
                    minListSize = len(resultList)


            if minListSize :
                returnArray = numpy.zeros(minListSize * len(roiResultCounterList) * 7,dtype = numpy.double)
                returnArray[0] = float(minListSize)
                indexArray = 0
                for roiName,resultList in roiResultCounterList:
                    roi_id = self.__roiName2ID.get(roiName)
                    for result in resultList[:minListSize] :
                        returnArray[indexArray:indexArray+7] = (float(roi_id),
                                                                float(result.frameNumber),
                                                                result.sum,
                                                                result.average,
                                                                result.std,
                                                                result.minValue,
                                                                result.maxValue)
                        indexArray += 7
                return returnArray
        return numpy.array([],dtype = numpy.double)

#==================================================================
#
#    RoiCounterClass class definition
#
#==================================================================
class RoiCounterDeviceServerClass(PyTango.DeviceClass):

    #	 Class Properties
    class_property_list = {
        }


    #	 Device Properties
    device_property_list = {
        }


    #	 Command definitions
    cmd_list = {
        'addNames':
        [[PyTango.DevVarStringArray,"rois alias"],
         [PyTango.DevVarLongArray,"rois' id"]],
        'removeRois':
        [[PyTango.DevVarStringArray,"rois alias"],
         [PyTango.DevVoid,""]],
        'setRois':
        [[PyTango.DevVarLongArray,"roi vector [roi_id0,x0,y0,width0,height0,roi_id1,x1,y1,width1,heigh1,...]"],
         [PyTango.DevVoid,""]],
        'setArcRois':
        [[PyTango.DevVarDoubleArray,"roi arc vector [roi_id,centerX,centerY,rayon1,rayon2,angle_start,angle_end,...]"],
        [PyTango.DevVoid,""]],
        'getNames':
        [[PyTango.DevVoid,""],
         [PyTango.DevVarStringArray,"rois alias"]],
        'getRoiTypes':
        [[PyTango.DevVarStringArray,"rois alias"],
         [PyTango.DevVarStringArray,"rois types"]],
        'getRois':
        [[PyTango.DevVarStringArray,"rois alias"],
         [PyTango.DevVarLongArray,"roi vector [roi_id0,x0,y0,width0,height0,roi_id1,x1,y1,width1,heigh1,...]"]],
        'getArcRois':
        [[PyTango.DevVarStringArray,"rois alias"],
         [PyTango.DevVarDoubleArray,"roi vector [roi arc vector [roi_id,centerX,centerY,rayon1,rayon2,angle_start,angle_end,...]"]],
        'clearAllRois':
        [[PyTango.DevVoid,""],
         [PyTango.DevVoid,""]],
        'setMaskFile':
        [[PyTango.DevVarStringArray,"Full path of mask file"],
         [PyTango.DevVoid,""]],
        'readCounters':
        [[PyTango.DevLong,"from which frame"],
         [PyTango.DevVarDoubleArray,"roi_id,frame number,sum,average,std,min,max,..."]],
        'Start':
        [[PyTango.DevVoid,""],
         [PyTango.DevVoid,""]],
        'Stop':
        [[PyTango.DevVoid,""],
         [PyTango.DevVoid,""]],
        }


    #	 Attribute definitions
    attr_list = {
        'BufferSize':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ_WRITE]],
        'CounterStatus':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ]],
        'RunLevel':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ_WRITE]],
        }


#------------------------------------------------------------------
#    RoiCounterDeviceServerClass Constructor
#------------------------------------------------------------------
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name);



_control_ref = None
def set_control_ref(control_class_ref) :
    global _control_ref
    _control_ref= control_class_ref

def get_tango_specific_class_n_device() :
    return RoiCounterDeviceServerClass,RoiCounterDeviceServer
