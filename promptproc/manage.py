#!/usr/bin/env python
####################################################################
#   THIS FILE HAS BEEN CUSTOMIZED, KEEP IT IN THE REPO   -mxp-     #
#   For example:                                                   #
#     - startup: initialize workflows                              #
####################################################################


import os
import sys



if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "promptproc.settings")
    
    import promptproc.startup as startup
    # Run the startup/initialization:
    startup.run()
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # Ensure that the issue is really that Django is missing
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
