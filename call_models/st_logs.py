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
    # Initializes a custom log handler with a Streamlit container for displaying logs
    def __init__(self, container, maxlen:int=15, debug:bool=False):
        super().__init__()
        # Store the Streamlit container for log output
        self.container = container
        self.debug = debug
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])') # Regex to remove ANSI codes
        self.log_area = self.container.empty() # Prepare an empty conatiner for log output

        self.buffer = deque(maxlen=maxlen)
        self._n = 0
        
    def n_elems(self, verb:bool=False):
        ''' return a string with num elements seen and num elements in buffer '''
        if verb:
            return f"total: {self._n}|| in buffer:{len(self.buffer)}"

        return f"{self._n}||{len(self.buffer)}"

    def emit(self, record):
        self._n += 1
        msg = f"[{self._n}]" + self.format(record)
        self.buffer.append(msg)
        clean_msg = self.ansi_escape.sub('', msg)  # Strip ANSI codes
        if self.debug:
            self.log_area.markdown(clean_msg)
                
    def clear_logs(self):
        self.log_area.empty()  # Clear previous logs
        self.buffer.clear()

# Set up logging to capture all info level logs from the root logger
@st.cache_resource
def setup_logging(level: int=logging.INFO, buffer_len:int=15):
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

def parse_log_buffer(log_contents: deque) -> list:
    ''' convert log buffer to a list of dictionaries '''
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

def something():
    '''function to demo adding log entries'''
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
        button = st.button("do something", on_click=something)
    with c2:
        st.info(f"Length of records: {len(records)}")
    #tab = st.table(records)
    tab = st.dataframe(records[::-1], use_container_width=True)  # scrollable, selectable.
