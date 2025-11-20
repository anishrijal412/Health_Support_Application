import io
import os
import sys
from datetime import datetime
import unittest
from flask import Blueprint, jsonify, render_template, send_from_directory
from openpyxl import Workbook

unit_test = Blueprint('unit_test', __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEST_DIR = os.path.join(BASE_DIR, 'tests')
REPORTS_DIR = os.path.join(BASE_DIR, 'instance', 'reports')
REPORT_FILENAME = 'unit_test_report.xlsx'

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


class RecordingTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_records = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.test_records.append({
            'name': self.getDescription(test),
            'status': 'Success',
            'message': 'Test passed'
        })

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.test_records.append({
            'name': self.getDescription(test),
            'status': 'Failure',
            'message': self._exc_info_to_string(err, test)
        })

    def addError(self, test, err):
        super().addError(test, err)
        self.test_records.append({
            'name': self.getDescription(test),
            'status': 'Error',
            'message': self._exc_info_to_string(err, test)
        })


class RecordingTextTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return RecordingTestResult(self.stream, self.descriptions, self.verbosity)


def _ensure_reports_dir():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    return REPORTS_DIR


def _save_report(records):
    reports_dir = _ensure_reports_dir()
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Test Results'

    worksheet.append(['Test Name', 'Status', 'Message', 'Timestamp'])
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for record in records:
        worksheet.append([
            record.get('name', 'Unknown Test'),
            record.get('status', 'Unknown'),
            record.get('message', ''),
            timestamp
        ])

    workbook.save(os.path.join(reports_dir, REPORT_FILENAME))


def _run_tests(test_modules=None):
    loader = unittest.TestLoader()

    if test_modules:
        suites = [loader.loadTestsFromName(name) for name in test_modules]
        suite = unittest.TestSuite(suites)
    else:
        suite = loader.discover(start_dir=TEST_DIR)

    stream = io.StringIO()
    runner = RecordingTextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)

    _save_report(result.test_records)

    return {
        'success': True,
        'file_url': f'/download/{REPORT_FILENAME}',
        'results': result.test_records,
        'output': stream.getvalue()
    }


@unit_test.route('/unit-test')
def unit_test_page():
    return render_template('unit_test.html')


@unit_test.route('/run-all-tests', methods=['POST'])
def run_all_tests():
    return jsonify(_run_tests())


@unit_test.route('/run-login-test', methods=['POST'])
def run_login_test():
    return jsonify(_run_tests(['tests.test_login']))


@unit_test.route('/run-forum-test', methods=['POST'])
def run_forum_test():
    return jsonify(_run_tests(['tests.test_forum']))


@unit_test.route('/run-appointment-test', methods=['POST'])
def run_appointment_test():
    return jsonify(_run_tests(['tests.test_appointment']))


@unit_test.route('/run-profile-test', methods=['POST'])
def run_profile_test():
    return jsonify(_run_tests(['tests.test_profile']))


@unit_test.route(f'/download/{REPORT_FILENAME}')
def download_report():
    reports_dir = _ensure_reports_dir()
    return send_from_directory(reports_dir, REPORT_FILENAME, as_attachment=True)