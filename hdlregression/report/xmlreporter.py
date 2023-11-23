#
# Copyright (c) 2022 by HDLRegression Authors.  All rights reserved.
# Licensed under the MIT License; you may not use this file except in compliance with the License.
# You may obtain a copy of the License at https://opensource.org/licenses/MIT.
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.
#
# HDLRegression AND ANY PART THEREOF ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH UVVM OR THE USE OR OTHER DEALINGS IN HDLRegression.
#

from datetime import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom
from .hdlreporter import HDLReporter

class XMLReporter(HDLReporter):
    '''
    HDLReporter sub-class for documenting testcase run
    to an XML file.
    '''

    def __init__(self, project=None, filename=None):
        super().__init__(project=project, filename=filename)

    def write_to_file(self) -> None:
        '''
        Writes regression run result to file in JUnit XML format (see url):
        https://github.com/testmoapp/junitxml
        '''

        # Should use _time_of_run() but it returns None it seems
        #time_of_run = str(self._time_of_run())
        time_of_run = datetime.now().isoformat()
        passing_tests, fail_tests, not_run_tests = self.project.get_results()
        num_tests = len(passing_tests) + len(fail_tests) + len(not_run_tests)

        report = ET.Element("testsuites", attrib={'name': "HDLRegression simulation run",
                                                  'tests': str(num_tests),
                                                  'failures': str(len(fail_tests)),
                                                  'skipped': str(len(not_run_tests)),
                                                  'time': str(self._time_of_sim()),
                                                  'timestamp': time_of_run})

        testsuite = ET.SubElement(report, "testsuite", attrib={'name': 'All'})

        for test in passing_tests:
            ET.SubElement(testsuite, "testcase", attrib={'name': test})

        for test in fail_tests:
            fail_elem = ET.SubElement(testsuite, "testcase", attrib={'name': test})
            ET.SubElement(fail_elem, "failure", attrib={'message': 'Test case failed.'})

        for test in not_run_tests:
            skip_elem = ET.SubElement(testsuite, "testcase", attrib={'name': test})
            ET.SubElement(skip_elem, "skipped", attrib={'message': 'Test was skipped.'})

        # Do not create report if no test was run
        if self._check_test_was_run():
            # Convert the XML tree to a prettified string
            xml_string = ET.tostring(report, encoding="unicode", method="xml")
            formatted_xml = minidom.parseString(xml_string).toprettyxml(indent="    ")

            # Write the formatted XML string to file
            with open(self.get_full_filename(), 'w') as lf:
                lf.write(formatted_xml)
