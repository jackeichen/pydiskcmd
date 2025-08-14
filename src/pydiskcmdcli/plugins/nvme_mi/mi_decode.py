from pydiskcmdlib.utils.converter import decode_bits,scsi_ba_to_int

def decode_subsys_health_status(data):
    """
    Decode the Subsystem Health Status data.

    :param data: The raw data bytes.
    :return: A dictionary containing the decoded values.
    """
    result = {"NVM Subsystem Status": {},
              "Smart Warnings": None,
              "Composite Temperature": None,
              "Percentage Drive Life Used": None,
              "Composite Controller Status": None,
              }
    result["NVM Subsystem Status"]["P1LA"] = data[0] & 0x04
    result["NVM Subsystem Status"]["P0LA"] = data[0] & 0x08
    result["NVM Subsystem Status"]["RNR"] = data[0] & 0x10
    result["NVM Subsystem Status"]["DF"] = data[0] & 0x20
    ##
    result["Smart Warnings"] = data[1]
    result["Composite Temperature"] = data[2]
    result["Percentage Drive Life Used"] = data[3]
    result["Composite Controller Status"] = data[4] + (data[5] << 8)
    return result
