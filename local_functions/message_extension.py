#!/usr/bin/python
import hashpumpy


class mac:
    def __init__(self, message, mac, key_length):
        """
        :param message: The original message
        :param mac: The original mac, it could be anything really
        :param key_length: The keylength of the private key
        """
        self.key_length = int(key_length)
        self.message = message
        self.mac = mac
        pass

    def check_extension(self, submit_extension, submit_message, submit_digest):
        """
        :param submit_extension: The competitor's addition to the message
        :param submit_message: The  competitor's extended message
        :param submit_digest: The  competitor's digest of the extended message
        :return: True if they did it correctly, false if otherwise
        """
        correct_message, correct_digest = self.mac_attack(submit_extension)
        if submit_message == correct_message and submit_digest == correct_digest:
            return True
        else:
            return False

    def mac_attack(self, extension):
        """
        :param extension: The text you will add to the message
        :return: The extended message and its hash
        """
        hmac = hashpumpy.hashpump(self.mac, self.message, extension, self.key_length)
        digest = hmac[0]
        message = "".join("{:02x}".format(ord(c)) for c in hmac[1].decode('cp437'))
        return message, digest
