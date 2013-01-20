import struct
import sys

sys.path.append('/Users/jeremy/src/make-me/vendor/s3g')
import makerbot_driver

TOOL_ACTION = makerbot_driver.host_action_command_dict['TOOL_ACTION_COMMAND']


class RawFileReader(makerbot_driver.FileReader.FileReader):
    """Like FileReader, but also return the raw strings from the s3g file.

    FileReader.ReadFile returns a list of commands, where each command is a
    list containing the command's identifier and its
    arguments. RawFileReader.ReadFile also returns a list of commands, but
    each command is paired with the string from the s3g file representing
    the command.

    This is useful for reading an s3g file and then sending the commands to
    a machine using s3g.send_action_payload.

    This code is mostly copied from FileReader, with a few changes in order
    to pass on the strings.
    """

    def ParseOutParameters(self, formatString):
        """Reads and decodes a certain number of bytes using a specific
        format string from the input s3g file

        @param string formatString: The format string we will unpack from
          the file
        @return a 2-tuple containing the string read out of the file, and
          a list of objects unpacked from the input s3g file
        """
        returnParams = []
        bytes = []
        for formatter in formatString:
            if formatter == 's':
                b = self.GetStringBytes()
                formatString = '<' + str(len(b)) + formatter
            else:
                b = self.ReadBytes(struct.calcsize(formatter))
                formatString = '<' + formatter
            bytes.append(b)
            returnParams.append(self.ParseParameter(formatString, b))
        return ''.join(bytes), returnParams

    def ParseToolAction(self, cmd):
        if cmd != TOOL_ACTION:
            self._log.error(
                '{"event":"cmd_is_not_tool_action_cmd", "bad_cmd":%s}', cmd)
            raise makerbot_driver.FileReader.NotToolActionCmdError
        bytes, data = self.ParseOutParameters(
            makerbot_driver.FileReader.hostFormats[cmd])
        slaveCmd = data[1]
        try:
            extra_bytes, extra_data = self.ParseOutParameters(
                makerbot_driver.FileReader.slaveFormats[slaveCmd])
            bytes += extra_bytes
            data.extend(extra_data)
        except KeyError:
            self._log.error(
                '{"event":"bad_slave_cmd", "bad_cmd":%s}', slaveCmd)
            raise makerbot_driver.FileReader.BadSlaveCommandError(slaveCmd)
        return bytes, data

    def ParseNextPayload(self):
        """Gets the next command and returns the parsed commands and
        associated parameters

        @return a 2-tuple containing the string read out of the file, and
          a list of the commands.
        """
        cmd = self.GetNextCommand()
        if cmd == TOOL_ACTION:
            bytes, params = self.ParseToolAction(cmd)
        else:
            bytes, params = self.ParseHostAction(cmd)
        return struct.pack('<B', cmd) + bytes, [cmd] + params

    def ReadFile(self):
        """Reads from an s3g file until it cant read anymore

        @return payloads: A list of 2-tuples, one per payload, where the
          first item in the 2-tuple is the string read out of the file, and
          the second is a list representing the command and its parameters.
        """
        payloads = []
        try:
            self._log.debug('{"event":"reading_bytes_from_file", "file":%s}',
                            str(self.file))
            while True:
                payload = self.ParseNextPayload()
                payloads.append(payload)
        # TODO: We aren't catching partial packets at the end of files here.
        except makerbot_driver.FileReader.EndOfFileError:
            self._log.debug('{"event":"done_reading_file"}')
            return payloads
