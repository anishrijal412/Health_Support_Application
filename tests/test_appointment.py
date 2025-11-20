import unittest


class AppointmentTests(unittest.TestCase):
    def test_success_case(self):
        self.assertGreaterEqual(2, 1, "Appointment scheduling success simulation")

    def test_failure_case(self):
        self.assertEqual('confirmed', 'pending', "Simulated appointment failure scenario")


if __name__ == '__main__':
    unittest.main()