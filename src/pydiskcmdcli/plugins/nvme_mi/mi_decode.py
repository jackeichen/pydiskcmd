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
    result["NVM Subsystem Status"]["P1LA"] = (data[0] >> 2) & 0x01
    result["NVM Subsystem Status"]["P0LA"] = (data[0] >> 3) & 0x01
    result["NVM Subsystem Status"]["RNR"] = (data[0] >> 4) & 0x01
    result["NVM Subsystem Status"]["DF"] = (data[0] >> 5) & 0x01
    ##
    result["Smart Warnings"] = data[1]
    result["Composite Temperature"] = data[2]
    result["Percentage Drive Life Used"] = data[3]
    result["Composite Controller Status"] = data[4] + (data[5] << 8)
    return result

def decode_ctrl_health_status(data):
    """
    Decode the Controller Health Status data.

    :param data: The raw data bytes.
    :return: A dictionary containing the decoded values.
    """
    result = []
    for i in range(0, len(data), 16):
        temp_data = data[i:i+16]
        temp_result = {}
        temp_result["Controller Identifier"] = temp_data[0] + (temp_data[1] << 8)
        temp_result["Controller Status"] = temp_data[2] + (temp_data[3] << 8)
        temp_result["Composite Temperature"] = temp_data[4] + (temp_data[5] << 8)
        temp_result["Percentage Used"] = temp_data[6]
        temp_result["Available Spare"] = temp_data[7]
        temp_result["Critical Warning"] = temp_data[8]
        temp_result["Controller Health Status Changed"] = temp_data[9] + (temp_data[10] << 8)
        result.append(temp_result)
    return result

