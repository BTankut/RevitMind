# dependencies
import os
import json

print("Loading user_interface.py from:", os.path.abspath(__file__))

import clr
clr.AddReference('System')
clr.AddReference('System.Net')
clr.AddReference('System.Threading')
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')
clr.AddReference('PresentationCore')
clr.AddReference('PresentationFramework')
clr.AddReference('System.Windows.Forms')
clr.AddReference('RevitAPI')

print("Debug - Loading Revit API modules...")
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, UnitUtils

print("Debug - Loading Revit exceptions...")
from Autodesk.Revit.Exceptions import InvalidOperationException
from System.Windows.Controls.Primitives import BulletDecorator
from System.Windows.Media.Imaging import BitmapImage
from System.Windows.Media.Animation import DiscreteObjectKeyFrame
from System.Windows.Controls import Image
from System.Windows import ResourceDictionary
from System import Uri

from System import String
from System.Net import WebClient, WebRequest
from System.Text import Encoding
from System.IO import StreamReader
from System.Threading import Thread
from System.Net import WebException

from pyrevit import forms
from pyrevit import UI
from pyrevit import script

from custom_functions import ContextData


class CustomizableEvent:
    def __init__(self):
        custom_handler = _CustomHandler()
        custom_handler.customizable_event = self
        self.custom_event = UI.ExternalEvent.Create(custom_handler)
        self.function_or_method = None
        self.args = ()
        self.kwargs = {}

    def _raised_method(self):
        self.function_or_method(*self.args, **self.kwargs)

    def raise_event(self, function_or_method, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.function_or_method = function_or_method
        self.custom_event.Raise()


class _CustomHandler(UI.IExternalEventHandler):
    def __init__(self):
        self.customizable_event = None

    def Execute(self, application):
        try:
            self.customizable_event._raised_method()
        except InvalidOperationException:
            print("InvalidOperationException caught")

    def GetName(self):
        return "Execute function in IExternalHandler"


custom_event = CustomizableEvent()


class CustomWindow(forms.WPFWindow):
    def __init__(self):
        self.state = Custom_Window_State()
        self.current_dir = os.path.dirname(__file__)
        self.output = script.get_output()
        self.logger = script.get_logger()
        self.Uid = "ClippyAIWindow"  # Add unique ID for window tracking

    def setup(self):
        pass

    def update_state(self, new_state):
        self.state = new_state
        self.render_custom_ui()
        self.show()

    def render_custom_ui(self):
        try:
            # Update debug display
            temphtml_path = os.path.join(self.current_dir, 'temp.html')
            self.output.save_contents(temphtml_path)
            htmlContent = Read_file_incurrent_directory_to_string(temphtml_path)    
            self.DebugDisplay.NavigateToString(htmlContent)

            # Process messages
            messages = []
            for status, message in self.state.data:
                try:
                    # Handle bytes or string
                    if isinstance(message, bytes):
                        message = message.decode('utf-8')
                    elif message is None:
                        continue
                        
                    # Format based on status
                    if status == 'error':
                        messages.append("Error: " + str(message))
                    elif status == 'info':
                        messages.append("Info: " + str(message))
                    elif status == 'message':
                        messages.append(str(message))
                    else:
                        messages.append(str(message))
                except Exception as e:
                    print("Error processing message:", str(e))
                    continue

            # Update text display
            if messages:
                formatted_display = '\n'.join(messages)
                print("Debug - Formatted display:", formatted_display)
                self.myTextBlock.Text = formatted_display
            else:
                self.myTextBlock.Text = ""
        except Exception as e:
            print("Error in render_custom_ui:", str(e))
            self.myTextBlock.Text = "Error displaying messages"

    def click_submit(self, sender, e):
        custom_event.raise_event(query_chat_gpt, self)


class Custom_Window_State():
    def __init__(self):
        self.data = []


def Read_file_incurrent_directory_to_string(file_path):
     try:
          with open(file_path, 'r') as file:
               return file.read()
     except Exception as e:
        print("Error reading file: %s" % str(e))
        return None


def send_request(url, data):
    """Send a request with proper encoding"""
    try:
        json_data = json.dumps(data)
        encoded_data = Encoding.UTF8.GetBytes(json_data)
        
        request = WebRequest.Create(url)
        request.Method = "POST"
        request.ContentType = "application/json"
        request.ContentLength = len(encoded_data)
        
        request_stream = request.GetRequestStream()
        request_stream.Write(encoded_data, 0, len(encoded_data))
        request_stream.Close()
        
        response = request.GetResponse()
        response_stream = response.GetResponseStream()
        reader = StreamReader(response_stream)
        return reader.ReadToEnd()
    except Exception as e:
        print("Error in send_request: %s" % str(e))
        raise


def prepare_request_data(input_string):
    """Prepare request data"""
    if isinstance(input_string, bytes):
        input_string = input_string.decode('utf-8')
    return {"client": str(input_string)}


def handle_response(response_text):
    """Parse JSON response"""
    if isinstance(response_text, bytes):
        response_text = response_text.decode('utf-8')
    return json.loads(response_text)


def query_chat_gpt(window):    
    state = Custom_Window_State()

    # Get input
    input_string = window.MyTextBox.Text
    if input_string == "enter prompt...":
        window.FindName("myTextBlock").Text = "CANT USE DEFAULT STRING"
        return

    # Show processing
    window.FindName("myTextBlock").Text = "Processing..."
    state = Custom_Window_State()

    # Server config
    url = 'http://127.0.0.1:8080/'
    max_attempts = 3
    attempt = 1

    # Try to get response
    while attempt <= max_attempts:
        try:
            # Prepare request
            request_data = prepare_request_data(input_string)
            print("Info: Sending data to server: %s" % json.dumps(request_data))
            
            # Send request and get response
            response_text = send_request(url, request_data)
            response = handle_response(response_text)
            
            # Get response text and type
            response_text = str(response["response"])
            response_type = str(response["type"])
            print("Response: %s (Type: %s)" % (response_text, response_type))
            
            # Handle MISSING responses
            if "MISSING" in response_text:
                missing_text = response_text.split("-")[1]
                state.data.append(('info', missing_text))
                window.update_state(state)
                return
            
            # Handle code responses
            if response_type == "code":
                try:
                    # Prepare Revit API namespace
                    namespace = globals().copy()
                    namespace.update({
                        'clr': clr,
                        '__revit__': __revit__,
                        'BuiltInCategory': BuiltInCategory,
                        'FilteredElementCollector': FilteredElementCollector,
                        'UnitUtils': UnitUtils
                    })
                    # Execute code
                    exec(response_text, namespace)
                    # Show success message
                    state.data.append(('successful', 'Code executed successfully'))
                except Exception as exec_error:
                    print("Error executing code: %s" % str(exec_error))
                    state.data.append(('error', str(exec_error)))
            # Handle message responses
            else:
                state.data.append(('message', response_text))
            
            window.update_state(state)
            return
        
        except Exception as e:
            print("Error: %s" % str(e))
            state.data.append(('error', str(e)))
            window.update_state(state)
            attempt += 1
            if attempt > max_attempts:
                state.data.append(('failure', "Maximum attempts reached"))
                window.update_state(state)
                break
