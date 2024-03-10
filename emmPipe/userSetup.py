import os
print('Loading userSetup.py...')
from .dev.utils import create_reload_shelf_button


print('Setting development mode...')
if os.getenv['EMMPIPE_MODE'] == 'Production':
    create_reload_shelf_button(shelf_name="emmPipe", button_name="reload", module_to_reload='emmPipe')
