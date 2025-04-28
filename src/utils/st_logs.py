from typing import List
import logging
from datetime import datetime
import re
from collections import deque

import streamlit as st

# some discussions with code snippets from:
# https://discuss.streamlit.io/t/capture-and-display-logger-in-ui/69136

# configure log parsing (seems to need some tweaking)
_log_n_re = r'\[(\d+)\]'
_log_date_re = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})'
_log_mod_re = r'(\w+(?:\.\w+)*|__\w+__|<\w+>)'
_log_func_re = r'(\w+|<\w+>)'
_log_level_re = r'(\w+)'
_log_msg_re = '(.*)'
_sep = r' - '

log_pattern = re.compile(_log_n_re + _log_date_re + _sep + _log_mod_re + _sep + 
    _log_func_re + _sep + _log_level_re + _sep + _log_msg_re)


class StreamlitLogHandler(logging.Handler):
    """
    Custom Streamlit log handler to display logs in a Streamlit container

    A custom logging handler for Streamlit applications that displays log
    messages in a Streamlit container.

    Attributes:
        container (streamlit.DeltaGenerator): The Streamlit container where log messages will be displayed.
        debug (bool): A flag to indicate whether to display debug messages.
        ansi_escape (re.Pattern): A compiled regular expression to remove ANSI escape sequences from log messages.
        log_area (streamlit.DeltaGenerator): An empty Streamlit container for log output.
        buffer (collections.deque): A deque buffer to store log messages with a maximum length.
        _n (int): A counter to keep track of the number of log messages seen.

    Methods:
        __init__(container, maxlen=15, debug=False):
            Initializes the StreamlitLogHandler with a Streamlit container, buffer length, and debug flag.
        n_elems(verb=False):
            Returns a string with the total number of elements seen and the number of elements in the buffer.
            If verb is True, returns a verbose string; otherwise, returns a concise string.
        emit(record):
            Processes a log record, formats it, appends it to the buffer, and displays it in the Streamlit container.
            Strips ANSI escape sequences from the log message if present.
        clear_logs():
            Clears the log messages from the Streamlit container and the buffer.
    """
    # Initialize a custom log handler with a Streamlit container for displaying logs
    def __init__(self, container, maxlen:int=15, debug:bool=False):
        #TODO: find the type for streamlit generic containers
        super().__init__()
        # Store the Streamlit container for log output
        self.container = container
        self.debug = debug
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])') # Regex to remove ANSI codes
        self.log_area = self.container.empty() # Prepare an empty conatiner for log output

        self.buffer = deque(maxlen=maxlen)
        self._n = 0
        
    def n_elems(self, verb:bool=False) -> str:
        """
        Return a string with the number of elements seen and the number of elements in the buffer.

        Args:
            verb (bool): If True, returns a verbose string. Defaults to False.

        Returns:
            str: A string representing the total number of elements seen and the number of elements in the buffer.
        """
        if verb:
            return f"total: {self._n}|| in buffer:{len(self.buffer)}"

        return f"{self._n}||{len(self.buffer)}"

    def emit(self, record) -> None:
        '''put the record into buffer so it gets displayed

        Args:
            record (logging.LogRecord): The log record to process and display.
        
        '''
        self._n += 1
        msg = f"[{self._n}]" + self.format(record)
        self.buffer.append(msg)
        clean_msg = self.ansi_escape.sub('', msg)  # Strip ANSI codes
        if self.debug:
            self.log_area.markdown(clean_msg)
                
    def clear_logs(self) -> None:
        """
        Clears the log area and buffer.

        This method empties the log area to remove any previous logs and clears the buffer to reset the log storage.
        """
        self.log_area.empty()  # Clear previous logs
        self.buffer.clear()


def init_logging_session_states():
    """
    Initialise the session state variables for logging.
    """
    
    if "handler" not in st.session_state:
        st.session_state['handler'] = setup_logging()


# Set up logging to capture all info level logs from the root logger
@st.cache_resource
def setup_logging(level:int=logging.INFO, buffer_len:int=15) -> StreamlitLogHandler:
    """
    Set up logging for the application using Streamlit's container for log display.

    Args:
        level (int): The logging level (e.g., logging.INFO, logging.DEBUG). Default is logging.INFO.
        buffer_len (int): The maximum number of log messages to display in the Streamlit container. Default is 15.

    Returns:
        StreamlitLogHandler: The handler that has been added to the root logger.
    """
    root_logger = logging.getLogger() # Get the root logger
    log_container = st.container() # Create a container within which we display logs
    handler = StreamlitLogHandler(log_container, maxlen=buffer_len)
    handler.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    #if 'handler' not in st.session_state:
    #    st.session_state['handler'] = handler
    return handler


def parse_log_buffer(log_contents: deque) -> List[dict]:
    """
    Convert log buffer to a list of dictionaries for use with a streamlit datatable.

    Args:
        log_contents (deque): A deque containing log lines as strings.

    Returns:
        list: A list of dictionaries, each representing a parsed log entry with the following keys:
            - 'timestamp' (datetime): The timestamp of the log entry.
            - 'n' (str): The log entry number.
            - 'level' (str): The log level (e.g., INFO, ERROR).
            - 'module' (str): The name of the module.
            - 'func' (str): The name of the function.
            - 'message' (str): The log message.
    """

    j = 0
    records = []
    for line in log_contents:
        if line:  # Skip empty lines
            j+=1
            try:
                # regex to parsse log lines, with an example line:
                # '[1]2024-11-09 11:19:06,688 - task - run - INFO - 🏃 Running task '
                match = log_pattern.match(line)
                if match:
                    n, timestamp_str, name, func_name, level, message = match.groups()
                
                # Convert timestamp string to datetime
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                
                records.append({
                    'timestamp': timestamp,
                    'n': n,
                    'level': level,
                    'module': name, 
                    'func': func_name,
                    'message': message
                })
            except Exception as e:
                print(f"Failed to parse line: {line}")
                print(f"Error: {e}")
                continue
    return records

def demo_log_callback() -> None:
    '''basic demo of adding log entries as a callback function'''
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
    

if __name__ == "__main__":
    
    # create a logging handler for streamlit + regular python logging module
    handler = setup_logging()

    # get buffered log data and parse, ready for display as dataframe
    records = parse_log_buffer(handler.buffer)

    c1, c2 = st.columns([1, 3])
    with c1: 
        button = st.button("do something", on_click=demo_log_callback)
    with c2:
        st.info(f"Length of records: {len(records)}")
    #tab = st.table(records)
    tab = st.dataframe(records[::-1], use_container_width=True)  # scrollable, selectable.
