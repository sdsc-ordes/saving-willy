from transitions import Machine
from typing import List

OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
OKCYAN = '\033[96m'
FAIL = '\033[91m'
ENDC = '\033[0m'


FSM_STATES = ['doing_data_entry', 'data_entry_complete', 'data_entry_validated', 
              #'ml_classification_started', 
              'ml_classification_completed', 
              'manual_inspection_completed', 'data_uploaded']


class WorkflowFSM:
    def __init__(self, state_sequence: List[str]):
        self.state_sequence = state_sequence
        self.state_dict = {state: i for i, state in enumerate(state_sequence)}
        
        # Create state machine
        self.machine = Machine(
            model=self,
            states=state_sequence,
            initial=state_sequence[0],
        )

        # For each state (except the last), add a completion transition to the next state
        for i in range(len(state_sequence) - 1):
            current_state = state_sequence[i]
            next_state = state_sequence[i + 1]
            
            self.machine.add_transition(
                trigger=f'complete_{current_state}',
                source=current_state,
                dest=next_state,
                conditions=[f'is_in_{current_state}']
            )

            # Dynamically add a condition method for each state
            setattr(self, f'is_in_{current_state}',
                   lambda s=current_state: self.is_in_state(s))

        # Add callbacks for logging
        self.machine.before_state_change = self._log_transition
        self.machine.after_state_change = self._post_transition

    def is_in_state(self, state_name: str) -> bool:
        """Check if we're currently in the specified state"""
        return self.state == state_name

    def complete_current_state(self) -> bool:
        """
        Signal that the current state is complete.
        Returns True if state transition occurred, False otherwise.
        """
        current_state = self.state
        trigger_name = f'complete_{current_state}'
        
        if hasattr(self, trigger_name):
            try:
                trigger_func = getattr(self, trigger_name)
                trigger_func()
                return True
            except:
                return False
        return False

    # add a helper method, to find out if a given state has been reached/passed
    # we first need to get the index of the current state
    # then the index of the argument state
    # compare, and return boolean
    
    def is_in_state_or_beyond(self, state_name: str) -> bool:
        """Check if we have reached or passed the specified state"""
        if state_name not in self.state_dict:
            raise ValueError(f"Invalid state: {state_name}")
        
        return self.state_dict[state_name] <= self.state_dict[self.state]
    

    @property
    def current_state(self) -> str:
        """Get the current state name"""
        return self.state
    
    @property
    def current_state_index(self) -> int:
        """Get the current state index"""
        return self.state_dict[self.state]

    @property
    def num_states(self) -> int:
        return len(self.state_sequence)
 

    def _log_transition(self):
        # TODO: use logger, not printing. 
        self._cprint(f"[FSM] -> Transitioning from {self.current_state}")

    def _post_transition(self):
        # TODO: use logger, not printing. 
        self._cprint(f"[FSM] -| Transitioned to {self.current_state}")

    def _cprint(self, msg:str, color:str=OKCYAN):
        """Print colored message"""
        print(f"{color}{msg}{ENDC}")
