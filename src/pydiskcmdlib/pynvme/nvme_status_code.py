# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later

# Based nvme spec 1.4c
# Dict in type of (SCT, SC): Description
StatusCodeDescription = {
    (0, 0): "Successful Completion: The command completed without error.",
    (0, 0x01): "Invalid Command Opcode: A reserved coded value or an unsupported value in the command opcode field.",
    (0, 0x02): "Invalid Field in Command: A reserved coded value or an unsupported value in a defined field \
(other than the opcode field). This status code should be used unless another status code is \
explicitly specified for a particular condition. The field may be in the command parameters as part \
of the Submission Queue Entry or in data structures pointed to by the command parameters.",
    (0, 0x03): "Command ID Conflict: The command identifier is already in use. Note: It is implementation specific \
how many commands are searched for a conflict.",
    (0, 0x04): "Data Transfer Error: Transferring the data or metadata associated with a command had an error.",
    (0, 0x05): "Commands Aborted due to Power Loss Notification: Indicates that the command was aborted \
due to a power loss notification.",
    (0, 0x06): "Internal Error: The command was not completed successfully due to an internal error. Details on \
the internal device error should be reported as an asynchronous event. Refer to Figure 147 for \
Internal Error Asynchronous Event Information.",
    (0, 0x07): "Command Abort Requested: The command was aborted due to an Abort command being \
received that specified the Submission Queue Identifier and Command Identifier of this command.",
    (0, 0x08): "Command Aborted due to SQ Deletion: The command was aborted due to a Delete I/O \
Submission Queue request received for the Submission Queue to which the command was submitted.",
    (0, 0x09): "Command Aborted due to Failed Fused Command: The command was aborted due to the other \
command in a fused operation failing.",
    (0, 0x0A): "Command Aborted due to Missing Fused Command: The fused command was aborted due to \
the adjacent submission queue entry not containing a fused command that is the other command \
in a supported fused operation.",
    (0, 0x0B): "Invalid Namespace or Format: The namespace or the format of that namespace is invalid.",
    (0, 0x0C): "Command Sequence Error: The command was aborted due to a protocol violation in a multi-command \
sequence (e.g., a violation of the Security Send and Security Receive sequencing rules \
in the TCG Storage Synchronous Interface Communications protocol (refer to TCG Storage \
Architecture Core Specification)).",
    (0, 0x0D): "Invalid SGL Segment Descriptor: The command includes an invalid SGL Last Segment or SGL \
Segment descriptor. This may occur under various conditions.",
    (0, 0x0E): "Invalid Number of SGL Descriptors: There is an SGL Last Segment descriptor or an SGL \
Segment descriptor in a location other than the last descriptor of a segment based on the length \
indicated. This is also used for invalid SGLs in a command capsule (refer to NVMe over Fabrics \
specification).",
    (0, 0x0F): "Data SGL Length Invalid: This may occur if the length of a Data SGL is too short. This may occur \
if the length of a Data SGL is too long and the controller does not support SGL transfers longer than \
the amount of data to be transferred as indicated in the SGL Support field of the Identify Controller \
data structure.",
    (0, 0x10): "Metadata SGL Length Invalid: This may occur if the length of a Metadata SGL is too short. This \
may occur if the length of a Metadata SGL is too long and the controller does not support SGL \
transfers longer than the amount of data to be transferred as indicated in the SGL Support field of \
the Identify Controller data structure.",
    (0, 0x11): "SGL Descriptor Type Invalid: The type of an SGL Descriptor is a type that is not supported by the \
controller, or the combination of type and subtype is not supported by the controller.",
    (0, 0x12): "Invalid Use of Controller Memory Buffer: The attempted use of the Controller Memory Buffer is \
not supported by the controller.",
    (0, 0x13): "PRP Offset Invalid: The Offset field for a PRP entry is invalid. This may occur when there is a PRP \
entry with a non-zero offset after the first entry or when the Offset field in any PRP entry is not dword aligned",
    (0, 0x14): "Atomic Write Unit Exceeded: The length specified exceeds the atomic write unit size.",
    (0, 0x15): "Operation Denied: The command was denied due to lack of access rights. Refer to the appropriate \
security specification (e.g., TCG Storage Interface Interactions Specification). For media access \
commands, the Access Denied status code should be used instead.",
    (0, 0x16): "SGL Offset Invalid: The offset specified in a descriptor is invalid. This may occur when using \
capsules for data transfers in NVMe over Fabrics implementations and an invalid offset in the \
capsule is specified.",
    (0, 0x17): "Reserved",
    (0, 0x18): "Host Identifier Inconsistent Format: The NVM subsystem detected the simultaneous use of 64-\
bit and 128-bit Host Identifier values on different controllers.",
    (0, 0x19): "Keep Alive Timer Expired: The Keep Alive Timer expired.",
    (0, 0x1A): "Keep Alive Timeout Invalid: The Keep Alive Timeout value specified is invalid. This may be due \
to an attempt to specify a value of 0h on a transport that requires the Keep Alive feature to be \
enabled. This may be due to the value specified being too large for the associated NVMe Transport \
as defined in the NVMe Transport binding specification.",
    (0, 0x1B): "Command Aborted due to Preempt and Abort: The command was aborted due to a Reservation \
Acquire command with the Reservation Acquire Action (RACQA) set to 010b (Preempt and Abort).",
    (0, 0x1C): "Sanitize Failed: The most recent sanitize operation failed and no recovery action has been \
successfully completed.",
    (0, 0x1D): "Sanitize In Progress: The requested function (e.g., command) is prohibited while a sanitize \
operation is in progress.",
    (0, 0x1E): "SGL Data Block Granularity Invalid: The Address alignment or Length granularity for an SGL \
Data Block descriptor is invalid. This may occur when a controller supports dword granularity only \
and the lower two bits of the Address or Length are not cleared to 00b.",
    (0, 0x1F): "Command Not Supported for Queue in CMB: The implementation does not support submission \
of the command to a Submission Queue in the Controller Memory Buffer or command completion\
to a Completion Queue in the Controller Memory Buffer.",
    (0, 0x20): "Namespace is Write Protected: The command is prohibited while the namespace is write \
protected as a result of a change in the namespace write protection state as defined by the \
Namespace Write Protection State Machine",
    (0, 0x21): "Command Interrupted: Command processing was interrupted and the controller is unable to \
successfully complete the command. The host should retry the command.",
    (0, 0): "Transient Transport Error: A transient transport error was detected. If the command is retried on \
the same controller, the command is likely to succeed. A command that fails with a transient \
transport error four or more times should be treated as a persistent transport error that is not likely \
to succeed if retried on the same controller.",
    (0, 0x80): "LBA Out of Range: The command references an LBA that exceeds the size of the namespace.",
    (0, 0x81): "Capacity Exceeded: Execution of the command has caused the capacity of the namespace to be \
exceeded. This error occurs when the Namespace Utilization exceeds the Namespace Capacity.",
    (0, 0x82): "Namespace Not Ready: The namespace is not ready to be accessed as a result of a condition \
other than a condition that is reported as an Asymmetric Namespace Access condition. The Do Not \
Retry bit indicates whether re-issuing the command at a later time may succeed.",
    (0, 0x83): "Reservation Conflict: The command was aborted due to a conflict with a reservation held on the \
accessed namespace.",
    (0, 0x84): "Format In Progress: A Format NVM command is in progress on the namespace. The Do Not \
Retry bit shall be cleared to '0' to indicate that the command may succeed if resubmitted.",
    (0x01, 0): "Completion Queue Invalid.",
    (0x01, 0x01): "Invalid Queue Identifier.",
    (0x01, 0x02): "Invalid Queue Size.",
    (0x01, 0x03): "Abort Command Limit Exceeded.",
    (0x01, 0x04): "Reserved.",
    (0x01, 0x05): "Asynchronous Event Request Limit Exceeded.",
    (0x01, 0x06): "Invalid Firmware Slot.",
    (0x01, 0x07): "Invalid Firmware Image.",
    (0x01, 0x08): "Invalid Interrupt Vector.",
    (0x01, 0x09): "Invalid Log Page.",
    (0x01, 0x0A): "Invalid Format.",
    (0x01, 0x0B): "Firmware Activation Requires Conventional Reset.",
    (0x01, 0x0C): "Invalid Queue Deletion.",
    (0x01, 0x0D): "Feature Identifier Not Saveable.",
    (0x01, 0x0E): "Feature Not Changeable.",
    (0x01, 0x0F): "Feature Not Namespace Specific.",
    (0x01, 0x10): "Firmware Activation Requires NVM Subsystem Reset.",
    (0x01, 0x11): "Firmware Activation Requires Controller Level Reset.",
    (0x01, 0x12): "Firmware Activation Requires Maximum Time Violation.",
    (0x01, 0x13): "Firmware Activation Prohibited",
    (0x01, 0x14): "Overlapping Range",
    (0x01, 0x15): "Namespace Insufficient Capacity",
    (0x01, 0x16): "Namespace Identifier Unavailable.",
    (0x01, 0x17): "Reserved.",
    (0x01, 0x18): "Namespace Already Attached.",
    (0x01, 0x19): "Namespace Is Private.",
    (0x01, 0x1A): "Namespace Not Attached.",
    (0x01, 0x1B): "Thin Provisioning Not Supported.",
    (0x01, 0x1C): "Controller List Invalid.",
    (0x01, 0x1D): "Device Self-test In Progress.",
    (0x01, 0x1E): "Boot Partition Write Prohibited.",
    (0x01, 0x1F): "Invalid Controller Identifier.",
    (0x01, 0x20): "Invalid Secondary Controller State.",
    (0x01, 0x21): "Invalid Number of Controller Resources.",
    (0x01, 0x22): "Invalid Resource Identifier.",
    (0x01, 0x23): "Sanitize Prohibited While Persistent Memory Region is Enabled.",
    (0x01, 0x24): "ANA Group Identifier Invalid.",
    (0x01, 0x25): "ANA Attach Failed.",
    (0x01, 0x80): "Conflicting Attributes.",
    (0x01, 0x81): "Invalid Protection Information.",
    (0x01, 0x82): "Attempted Write to Read Only Range.",
    (0x02, 0x80): "Write Fault: The write data could not be committed to the media.",
    (0x02, 0x81): "Unrecovered Read Error: The read data could not be recovered from the media.",
    (0x02, 0x82): "End-to-end Guard Check Error: The command was aborted due to an end-to-end guard check failure.",
    (0x02, 0x83): "End-to-end Application Tag Check Error: The command was aborted due to an end-to-end application tag check failure.",
    (0x02, 0x84): "End-to-end Reference Tag Check Error: The command was aborted due to an end-to-end reference tag check failure.",
    (0x02, 0x85): "Compare Failure: The command failed due to a miscompare during a Compare command.",
    (0x02, 0x86): "Access Denied: Access to the namespace and/or LBA range is denied due to lack of access rights. \
Refer to the appropriate security specification (e.g., TCG Storage Interface Interactions Specification).",
    (0x02, 0x87): "Deallocated or Unwritten Logical Block: The command failed due to an attempt to read from or \
verify an LBA range containing a deallocated or unwritten logical block",
    (0x03, 0): "Internal Path Error: The command was not completed as the result of a controller internal error \
that is specific to the controller processing the command. Retries for the request function should be based on the setting of the DNR bit",
    (0x03, 0x01): "Asymmetric Access Persistent Loss: The requested function (e.g., command) is not able to be \
performed as a result of the relationship between the controller and the namespace being in the \
ANA Persistent Loss state (refer to section 8.20.3.4). The command should not be re-submitted to the same controller",
    (0x03, 0x02): "Asymmetric Access Inaccessible: The requested function (e.g., command) is not able to be \
performed as a result of the relationship between the controller and the namespace being in the \
ANA Inaccessible state (refer to section 8.20.3.3). The command should not be re-submitted to the same controller.",
    (0x03, 0x03): "Asymmetric Access Transition: The requested function (e.g., command) is not able to be \
performed as a result of the relationship between the controller and the namespace transitioning \
between Asymmetric Namespace Access states (refer to section 8.20.3.5). The requested function \
should be retried after the transition is complete.",
    (0x03, 0x60): "Controller Pathing Error: A pathing error was detected by the controller.",
    (0x03, 0x70): "Host Pathing Error: A pathing error was detected by the host.",
    (0x03, 0x71): "Command Aborted By Host: The command was aborted as a result of host action (e.g., the host \
disconnected the Fabric connection).",
}
