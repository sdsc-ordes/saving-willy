
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
import time
import streamlit as st

def run(*args, **kwargs):
    # unpack the duration from the kwargs
    duration = kwargs.get('duration', 0.2)
    logger.info("🏃 Running task ")
    time.sleep(.2)
    logger.info("🥵 Still running task")
    time.sleep(0.1)
    logger.warning("⚠️ Task is taking longer than expected")
    #time.sleep(0.2)
    time.sleep(duration)
    logger.info("✅ Finished task")