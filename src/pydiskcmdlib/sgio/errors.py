class CheckConditionError(Exception):
    """The target is reporting an error.
    Send a Request Sense command to retrieve error information.
    See https://en.wikipedia.org/wiki/SCSI_check_condition for details.
    """

    def __init__(self, sense):
        super(CheckConditionError, self).__init__(
            'SCSI Check Condition: %s' % sense.hex()
        )
        self.sense = sense


class UnspecifiedError(Exception):
    """Something went wrong."""
