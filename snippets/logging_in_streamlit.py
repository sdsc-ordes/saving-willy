import logging
from datetime import datetime
import re
from collections import deque

import streamlit as st

import task

# some discussions with code snippets from:
# https://discuss.streamlit.io/t/capture-and-display-logger-in-ui/69136


class StreamlitLogHandler(logging.Handler):
    # Initializes a custom log handler with a Streamlit container for displaying logs
    def __init__(self, container, maxlen:int=15):
        super().__init__()
        # Store the Streamlit container for log output
        self.container = container
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
        self.log_area.markdown(clean_msg)
                
    def clear_logs(self):
        self.log_area.empty()  # Clear previous logs
        self.buffer.clear()

# Set up logging to capture all info level logs from the root logger
@st.cache_resource
def setup_logging():
    root_logger = logging.getLogger() # Get the root logger
    log_container = st.container() # Create a container within which we display logs
    handler = StreamlitLogHandler(log_container)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    if st.session_state.get('handler') is None:
        st.session_state['handler'] = handler
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
                match = re.match(r'\[(\d+)\](\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (\w+) - (\w+) - (.*)', line)
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

        
    # demo task
    with st.spinner("Running task"):
        task.run()
        
    # get buffered log data and parse, ready for display as dataframe
    log_contents = handler.buffer
    print(f"[D] log_contents: {log_contents}, n_elems: {len(log_contents)}")
    records = parse_log_buffer(log_contents)

    c1, c2 = st.columns([1, 3])
    with c1: 
        button = st.button("do something", on_click=something)
    with c2:
        st.info(f"Length of records: {len(records)}")
    #tab = st.table(records)
    tab = st.dataframe(records[::-1], use_container_width=True)  # scrollable, selectable.
