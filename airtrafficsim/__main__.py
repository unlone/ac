import sys
import os
from importlib import import_module

import airtrafficsim.server.server as server


def main():
    # Give error if BADA data is missing TODO: To be removed when OpenAP is implemented
    if len(os.listdir('data/performance/BADA/')) <= 1:
        raise IOError(
            "BADA folder is empty. Remember to put the BADA performance data into /data/performance/BADA/.")

    if len(sys.argv) > 1 and sys.argv[1] == '--headless':
        # Run user defined environment without UI: python -m airtrafficsim --headless <env name>
        Env = getattr(import_module('environment.' +
                      sys.argv[2], '...'), sys.argv[2])
        env = Env()
        env.run()
    else:
        # Run UI: python -m airtrafficsim
        server.run_server()


if __name__ == "__main__":
    main()
