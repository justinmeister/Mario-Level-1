__author__ = 'justinarmstrong'

from . import setup,tools
from .states import main_menu,load_screen,level1

def main():
    """Add states to control here."""
    run_it = tools.Control(setup.ORIGINAL_CAPTION)
    state_dict = {"MAIN_MENU": main_menu.Menu(),
                  "LOAD_SCREEN": load_screen.Load_Screen(),
                  "LEVEL1": level1.Level1()}

    run_it.setup_states(state_dict,"MAIN_MENU")
    run_it.main()