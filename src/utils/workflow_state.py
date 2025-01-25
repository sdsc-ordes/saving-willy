from transitions import Machine
from enum import Enum

OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
OKCYAN = '\033[96m'
FAIL = '\033[91m'
ENDC = '\033[0m'

# define the states
# 0. init 
# 1. data entry complete 
# 2. data entry validated
# 3. ML classification started (can be long running on batch)
# 4. ML classification completed
# 5. manual inspection / adjustment of classification completed
# 6. data uploaded

states = ['init', 'data_entry_complete', 'data_entry_validated', 'ml_classification_started', 'ml_classification_completed', 'manual_inspection_completed', 'data_uploaded']


# define an enum for the states, automatically giving integers according to the position in the list 
# - this is useful for the transitions
# maybe this needs to use setattr or similar
workflow_phases = Enum('StateEnum', {state: i for i, state in enumerate(states)}) 


class WorkflowState(Enum):
    INIT = 0
    DATA_ENTRY_COMPLETE = 1
    DATA_VALIDATED = 2
    #ML_STARTED = 3
    ML_COMPLETED = 3
    MANUAL_REVIEW_COMPLETE = 4
    UPLOADED = 5

    
# TODO: refactor the FSM to have explicit named states, and write a helper function to determine the next state and advance to it.
# this allows either triggering by name, or being a bit lazy and saying "advance" and it will go to the next state..
# maybe a cleaner way is to say completed('X') and then whatever the next state from X is can be taken. Instead of knowing 
# what the next state is (becausee that was supposed to be defined her in the specification, and not in each phase)
#
# also add a "did we pass stage X" function, by name. This will make it easy to choose what to present, what actions to do next etc.


class WorkflowFSM:
    def __init__(self):
        # Define states as strings (transitions requirement)
        self.states = [state.name for state in WorkflowState]
        # TODO: what is the point of the enum? I can just take the list and do an enumerate on it.??
        

        # Create state machine 
        self.machine = Machine(
            model=self,
            states=self.states,
            initial=WorkflowState.INIT.name,
        )

        # Add transitions for each state to the next state
        for i in range(len(self.states) - 1):
            self.machine.add_transition(
                trigger='advance',
                source=self.states[i],
                dest=self.states[i + 1]
            )

        # Add reset transition
        self.machine.add_transition(
            trigger='reset',
            source='*',
            dest=WorkflowState.INIT.name
        )

        # Add callbacks for logging
        self.machine.before_state_change = self._log_transition
        self.machine.after_state_change = self._post_transition

    def _cprint(self, msg:str, color:str=OKCYAN):
        """Print colored message"""
        print(f"{color}{msg}{ENDC}")
        

    def _advance_state(self):
        """Determine the next state based on current state"""
        current_idx = self.states.index(self.state)
        if current_idx < len(self.states) - 1:
            return self.states[current_idx + 1]
        return self.state  # Stay in final state if already there

    def _log_transition(self):
        # TODO: use logger, not printing. 
        self._cprint(f"[FSM] -> Transitioning from {self.state}")

    def _post_transition(self):
        # TODO: use logger, not printing. 
        self._cprint(f"[FSM] -| Transitioned to {self.state}")
    
    
    def advance(self):
        if self.state_number < len(self.states) - 1:
            self.trigger('advance')
        else:
            # maybe too aggressive to exception here?
            raise RuntimeError("Already at final state")  

    @property
    def state_number(self) -> int:
        """Get the numerical value of current state"""
        return self.states.index(self.state)

    @property
    def state_name(self) -> str:
        """Get the name of current state"""
        return self.state

    # add a property for the number of states
    @property
    def num_states(self) -> int:
        return len(self.states)
    