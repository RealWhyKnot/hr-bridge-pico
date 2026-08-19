import unittest

from hr_bridge_pico.serial_source import MICROPYTHON_PID, RP2_VID, find_port, parse_line


class FakePort:
    def __init__(self, device, vid, pid):
        self.device = device
        self.vid = vid
        self.pid = pid


class FindPortTest(unittest.TestCase):
    def test_prefers_the_micropython_interface(self):
        ports = [
            FakePort("COM3", 0x1234, 0x5678),
            FakePort("COM4", RP2_VID, 0x000A),
            FakePort("COM5", RP2_VID, MICROPYTHON_PID),
        ]
        self.assertEqual(find_port(ports), "COM5")

    def test_falls_back_to_any_raspberry_pi_device(self):
        ports = [FakePort("COM3", 0x1234, 0x5678), FakePort("COM4", RP2_VID, 0x000A)]
        self.assertEqual(find_port(ports), "COM4")

    def test_returns_none_when_no_board_is_present(self):
        self.assertIsNone(find_port([FakePort("COM3", 0x1234, 0x5678)]))

    def test_returns_none_for_an_empty_list(self):
        self.assertIsNone(find_port([]))

    def test_tolerates_ports_without_usb_identifiers(self):
        self.assertIsNone(find_port([FakePort("COM1", None, None)]))


class ParseLineTest(unittest.TestCase):
    def test_reads_a_plain_reading(self):
        self.assertEqual(parse_line(b"72\r\n"), 72)

    def test_accepts_text_as_well_as_bytes(self):
        self.assertEqual(parse_line("72\n"), 72)

    def test_drops_diagnostics(self):
        self.assertIsNone(parse_line(b"# subscribed\r\n"))

    def test_drops_blank_lines(self):
        self.assertIsNone(parse_line(b"\r\n"))

    def test_drops_partial_lines(self):
        self.assertIsNone(parse_line(b"7x\r\n"))

    def test_drops_zero(self):
        self.assertIsNone(parse_line(b"0\r\n"))

    def test_drops_implausible_values(self):
        self.assertIsNone(parse_line(b"9999\r\n"))

    def test_drops_undecodable_bytes(self):
        self.assertIsNone(parse_line(b"\xff\xfe\r\n"))


if __name__ == "__main__":
    unittest.main()
