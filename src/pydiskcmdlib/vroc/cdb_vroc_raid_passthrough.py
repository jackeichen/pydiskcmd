# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from .vroc_nvme_command import VROCNVMeCommand,win_ioctl
from pydiskcmdlib.exceptions import CommandReturnStatusError

class NVMePassThroughSRB(VROCNVMeCommand):
    _cdb_bits = {"HeaderLength": [0xFFFFFFFF, 0],  
                 "Signature": ['b', 4, 8],
                 "Timeout": [0xFFFFFFFF, 12],
                 "ControlCode": [0xFFFFFFFF, 16],
                 "ReturnCode":  [0xFFFFFFFF, 20],  #
                 "Length": [0xFFFFFFFF, 24], # 
                 # "VendorSpecific": [, 28], # length is 24
                 "OPC": [0xFF, 52],
                 "MIDV": [0xFF, 53],
                 "CID": [0xFFFF, 54],
                 "NSID": [0xFFFFFFFF, 56],
                 # "Reserved0": [0xFFFFFFFFFFFFFFFF, 60],
                 # "MPTR": [0xFFFFFFFFFFFFFFFF, 68],
                 # "PRP1": [0xFFFFFFFFFFFFFFFF, 76],
                 # "PRP2": [0xFFFFFFFFFFFFFFFF, 84],
                 "CDW10": [0xFFFFFFFF, 92],
                 "CDW11": [0xFFFFFFFF, 96],
                 "CDW12": [0xFFFFFFFF, 100],
                 "CDW13": [0xFFFFFFFF, 104],
                 "CDW14": [0xFFFFFFFF, 108],
                 "CDW15": [0xFFFFFFFF, 112],
                 # "CplEntry": [], # 116 - 132
                 "Direction": [0xFFFFFFFF, 132],
                 "QueueId": [0xFFFFFFFF, 136],
                 "DataBufferLen": [0xFFFFFFFF, 140],
                 "MetaDataLen": [0xFFFFFFFF, 144],
                 "ReturnBufferLen": [0xFFFFFFFF, 148],
                 "DataBuffer": [0xFF, 152],  # Should Not Set it
                }
    def __init__(self,
                 vroc_disk_id,
                 opc,
                 nsid,
                 cdw10,
                 cdw11,
                 cdw12,
                 cdw13,
                 cdw14,
                 cdw15,
                 direction,  # 0,1,2
                 queue_id,   # 0 means admin command, otherwise IO command
                 data_buffer_len, # data length
                 metadata_len=0,  # TODO, Not support now
                 ):
        VROCNVMeCommand.__init__(self)
        self.build_command(Signature=win_ioctl.NVME_RAID_SIG_STR,
                           ControlCode=win_ioctl.NVME_PASS_THROUGH_SRB_IO_CODE,
                           ReturnCode=vroc_disk_id,
                           OPC=opc,
                           NSID=nsid,
                           CDW10=cdw10,
                           CDW11=cdw11,
                           CDW12=cdw12,
                           CDW13=cdw13,
                           CDW14=cdw14,
                           CDW15=cdw15,
                           Direction=direction,
                           QueueId=queue_id,
                           DataBufferLen=data_buffer_len,
                           MetaDataLen=metadata_len,
                           )

    @property
    def cq_status(self):
        '''
        Compeletion Queue DWORD 3
        Need check after execute
        '''
        if self.cdb:
            return (self.cdb.CplEntry[3] >> 17)

    @property
    def cq_cmd_spec(self):
        '''
        Compeletion Queue DWORD 0
        Need check after execute
        '''
        if self.cdb:
            return self.cdb.CplEntry[0]

    def check_return_status(self, success_hint=False, fail_hint=True, raise_if_fail=False):
        '''
        Do Not Check it before command execute, it may failed in level 2.
        '''
        ## Level 1: Returned status of DeviceIoControl API
        #  This can be checked in pydiskcmdlib.device.win_device.WinIOCTLDevice.execute()
        ## Level 2: ReturnCode of SRB_IO_CONTROL structure
        if self.cdb.SrbIoCtrl.ReturnCode != 0 and fail_hint:
            print ("SrbIoCtrl->ReturnCode is %d" % self.cdb.SrbIoCtrl.ReturnCode)
            # raise CommandReturnDataCheckErr("SrbIoCtrl->ReturnCode is %d" % self.cdb.SrbIoCtrl.ReturnCode)
        ## Level 3: Status Field of Completion Entry
        SC = (self.cq_status & 0xFF)
        SCT = ((self.cq_status >> 8) & 0x07)
        CRD = ((self.cq_status >> 11) & 0x03)
        More = (self.cq_status >> 13 & 0x01)
        DNR = (self.cq_status >> 14 & 0x01)
        if SCT == 0 and SC == 0:
            if success_hint:
                print ("Command Success")
                print ('')
        else:
            if fail_hint:
                print ("Command failed, and details bellow.")
                format_string = "%-15s%-20s%-8s%s"
                print (format_string % ("Status Code", "Status Code Type", "More", "Do Not Retry"))
                print (format_string % (SC, SCT, More, DNR))
                print ('')
            if raise_if_fail:
                raise CommandReturnStatusError('Command Check Error')
        return SC,SCT
