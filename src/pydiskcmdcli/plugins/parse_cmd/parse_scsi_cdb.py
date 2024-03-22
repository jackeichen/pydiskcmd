# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
from typing import List,Dict
from pyscsi.pyscsi.scsi import *
from pyscsi.utils.converter import decode_bits
from pydiskcmdlib.pyscsi.scsi import *
from pyscsi.pyscsi.scsi_enum_command import (
    spc_opcodes,
    sbc_opcodes,
    ssc_opcodes,
    smc_opcodes,
    mmc_opcodes,
)

class SBCCDB(object):
    def __init__(self):
        self.spec_name = 'sbc'
        self.opcode = sbc_opcodes
        self.cdb_bits = {0xA1: ATAPassThrough12._cdb_bits,  # sbc
                        0x85: ATAPassThrough16._cdb_bits,  # sbc
                        0x83: (ExtendedCopy4._cdb_bits, 
                                ExtendedCopy5._cdb_bits), # spc, sbc, ssc
                        # 0x00: GetLBAStatus._cdb_bits,   # sbc
                        0x12: Inquiry._cdb_bits,   # spc, sbc, ssc, smc, mmc
                        0x15: ModeSelect6._cdb_bits, # spc, sbc, ssc, smc
                        0x1A: ModeSense6._cdb_bits,  # spc, sbc, ssc, smc
                        0x1C: ReceiveDiagnosticResults._cdb_bits,  # spc, sbc, ssc, smc
                        0x55: ModeSelect10._cdb_bits, # spc, sbc, ssc, smc
                        0x5A: ModeSense10._cdb_bits, # spc, sbc, ssc, smc
                        # 0x5E: PersistentReserveIn._cdb_bits, # TODO: spc,sbc,ssc,smc
                        0x5F: PersistentReserveOut._cdb_bits, # spc,sbc,ssc,smc
                        0x1E: PreventAllowMediumRemoval._cdb_bits, # spc, sbc, ssc, smc, mmc
                        0x28: Read10._cdb_bits,  # sbc, mmc
                        0xA8: Read12._cdb_bits,  # sbc, mmc
                        0x88: Read16._cdb_bits,  # sbc
                        0x25: ReadCapacity10._cdb_bits,  # sbc
                        0x10: ReadCapacity16._cdb_bits, # sbc
                        0xA0: ReportLuns._cdb_bits,  # spc, sbc, ssc, mmc, smc
                        # 0x0E: ReportPriority._cdb_bits,         # service_actions
                        # 0x00: ReportTargetPortGroups._cdb_bits, # service_actions
                        0x00: TestUnitReady._cdb_bits, # spc, sbc, ssc, smc, mmc
                        0x2A: Write10._cdb_bits,   # sbc, mmc
                        0xAA: Write12._cdb_bits,   # sbc, mmc
                        0x8A: Write16._cdb_bits,   # sbc
                        0x41: WriteSame10._cdb_bits, # sbc, 
                        0x93: WriteSame16._cdb_bits, # sbc, 
                        0x4D: LogSense._cdb_bits,    # spc, sbc, ssc, smc, 
                        0x35: SynchronizeCache10._cdb_bits, # sbc
                        0x91: SynchronizeCache16._cdb_bits, # sbc
                        0xA2: SecurityProtocolIn._cdb_bits, # sbc, mmc
                        # 0x00: Dummy._cdb_bits,
                        }


class SPCCDB(object):
    def __init__(self):
        self.spec_name = 'spc'
        self.opcode = spc_opcodes
        self.cdb_bits = {0x83: (ExtendedCopy4._cdb_bits, ExtendedCopy5._cdb_bits), # spc, sbc, ssc
                     0x12: Inquiry._cdb_bits,   # spc, sbc, ssc, smc, mmc
                     0x15: ModeSelect6._cdb_bits, # spc, sbc, ssc, smc
                     0x1A: ModeSense6._cdb_bits,  # spc, sbc, ssc, smc
                     0x1C: ReceiveDiagnosticResults._cdb_bits,  # spc, sbc, ssc, smc
                     0x55: ModeSelect10._cdb_bits, # spc, sbc, ssc, smc
                     0x5A: ModeSense10._cdb_bits, # spc, sbc, ssc, smc
                     # 0x5E: PersistentReserveIn._cdb_bits, # TODO: spc,sbc,ssc,smc
                     0x5F: PersistentReserveOut._cdb_bits, # spc,sbc,ssc,smc
                     0x1E: PreventAllowMediumRemoval._cdb_bits, # spc, sbc, ssc, smc, mmc
                     0xA0: ReportLuns._cdb_bits,  # spc, sbc, ssc, mmc, smc
                     # 0x0E: ReportPriority._cdb_bits,         # service_actions
                     # 0x00: ReportTargetPortGroups._cdb_bits, # service_actions
                     0x00: TestUnitReady._cdb_bits, # spc, sbc, ssc, smc, mmc
                     0x4D: LogSense._cdb_bits,    # spc, sbc, ssc, smc, 
                     # 0x00: Dummy._cdb_bits,
                     }


class SSCCDB(object):
    def __init__(self):
        self.spec_name = 'ssc'
        self.opcode = ssc_opcodes
        self.cdb_bits = {0x83: (ExtendedCopy4._cdb_bits, ExtendedCopy5._cdb_bits), # spc, sbc, ssc
                     0x12: Inquiry._cdb_bits,   # spc, sbc, ssc, smc, mmc
                     0x15: ModeSelect6._cdb_bits, # spc, sbc, ssc, smc
                     0x1A: ModeSense6._cdb_bits,  # spc, sbc, ssc, smc
                     0x1C: ReceiveDiagnosticResults._cdb_bits,  # spc, sbc, ssc, smc
                     0x55: ModeSelect10._cdb_bits, # spc, sbc, ssc, smc
                     0x5A: ModeSense10._cdb_bits, # spc, sbc, ssc, smc
                     # 0x5E: PersistentReserveIn._cdb_bits, # TODO: spc,sbc,ssc,smc
                     0x5F: PersistentReserveOut._cdb_bits, # spc,sbc,ssc,smc
                     0x1E: PreventAllowMediumRemoval._cdb_bits, # spc, sbc, ssc, smc, mmc
                     0xA0: ReportLuns._cdb_bits,  # spc, sbc, ssc, mmc, smc
                     # 0x0E: ReportPriority._cdb_bits,         # service_actions
                     # 0x00: ReportTargetPortGroups._cdb_bits, # service_actions
                     0x00: TestUnitReady._cdb_bits, # spc, sbc, ssc, smc, mmc
                     0x4D: LogSense._cdb_bits,    # spc, sbc, ssc, smc, 
                     # 0x00: Dummy._cdb_bits,
                     }


class SMCCDB(object):
    def __init__(self):
        self.spec_name = 'smc'
        self.opcode = smc_opcodes
        self.cdb_bits = {0xA6: ExchangeMedium._cdb_bits,    # smc
                     0x07: InitializeElementStatus._cdb_bits,  #smc
                     0x37: InitializeElementStatusWithRange._cdb_bits, #smc
                     0x12: Inquiry._cdb_bits,   # spc, sbc, ssc, smc, mmc
                     0x15: ModeSelect6._cdb_bits, # spc, sbc, ssc, smc
                     0x1A: ModeSense6._cdb_bits,  # spc, sbc, ssc, smc
                     0x1C: ReceiveDiagnosticResults._cdb_bits,  # spc, sbc, ssc, smc
                     0x55: ModeSelect10._cdb_bits, # spc, sbc, ssc, smc
                     0x5A: ModeSense10._cdb_bits, # spc, sbc, ssc, smc
                     0xA5: MoveMedium._cdb_bits,  # smc
                     0x1B: OpenCloseImportExportElement._cdb_bits, # smc
                     # 0x5E: PersistentReserveIn._cdb_bits, # TODO: spc,sbc,ssc,smc
                     0x5F: PersistentReserveOut._cdb_bits, # spc,sbc,ssc,smc
                     0x2B: PositionToElement._cdb_bits,   # smc
                     0x1E: PreventAllowMediumRemoval._cdb_bits, # spc, sbc, ssc, smc, mmc
                     0xB8: ReadElementStatus._cdb_bits,   # smc, 
                     0xA0: ReportLuns._cdb_bits,  # spc, sbc, ssc, mmc, smc
                     # 0x0E: ReportPriority._cdb_bits,         # service_actions
                     # 0x00: ReportTargetPortGroups._cdb_bits, # service_actions
                     0x00: TestUnitReady._cdb_bits, # spc, sbc, ssc, smc, mmc
                     0x4D: LogSense._cdb_bits,    # spc, sbc, ssc, smc
                     # 0x00: Dummy._cdb_bits,
                     }


class MMCCDB(object):
    def __init__(self):
        self.spec_name = 'mmc'
        self.opcode = mmc_opcodes
        self.cdb_bits = {0x12: Inquiry._cdb_bits,   # spc, sbc, ssc, smc, mmc
                     0x1E: PreventAllowMediumRemoval._cdb_bits, # spc, sbc, ssc, smc, mmc
                     0x28: Read10._cdb_bits,  # sbc, mmc
                     0xA8: Read12._cdb_bits,  # sbc, mmc
                     0xBE: ReadCd._cdb_bits,  # mmc
                     0x51: ReadDiscInformation._cdb_bits, # mmc
                     0xA0: ReportLuns._cdb_bits,  # spc, sbc, ssc, mmc, smc
                     # 0x0E: ReportPriority._cdb_bits,         # service_actions
                     # 0x00: ReportTargetPortGroups._cdb_bits, # service_actions
                     0x00: TestUnitReady._cdb_bits, # spc, sbc, ssc, smc, mmc
                     0x2A: Write10._cdb_bits,   # sbc, mmc
                     0xAA: Write12._cdb_bits,   # sbc, mmc
                     0xA2: SecurityProtocolIn._cdb_bits, # sbc, mmc
                     # 0x00: Dummy._cdb_bits,
                     }


def parse_cdb(cdb: List) -> Dict:
    all_cdb = (SBCCDB(), SPCCDB(), SSCCDB(), SMCCDB(), MMCCDB())
    ##
    #print ("Parse Command: %s" % ' '.join(cdb))
    ##
    cdb_opcode = cdb[0]
    ##
    parsed_cdb = {}
    for cdb_desp in all_cdb:
        for name,OpCode in cdb_desp.opcode.items():
            if cdb_opcode == OpCode.value:
                cdb_bits = cdb_desp.cdb_bits.get(cdb_opcode)
                if cdb_bits:
                    if isinstance(cdb_bits, tuple):
                        for _cdb_bits in cdb_bits:
                            ## get the cdb_bit length
                            cdb_length = 0
                            for i in _cdb_bits.values():
                                length = i[0]
                                offset = i[1]
                                while length:
                                    offset += 1
                                    length >> 8
                                cdb_length = max(cdb_length, offset)
                            if cdb_length == len(cdb):
                                break
                        else:
                            raise NotImplementedError("Command Not Implemented")
                    else:
                        _cdb_bits = cdb_bits
                    result = {}
                    decode_bits(bytearray(cdb), _cdb_bits, result)
                    parsed_cdb[cdb_desp.spec_name] = {"cdb_name": OpCode.name,
                                                      "opcode": cdb_opcode,
                                                      "cdb": result,
                                                      }
                else:
                    raise NotImplementedError("Command Not Implemented")
    return parsed_cdb
