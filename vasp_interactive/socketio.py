import os
import json
from pathlib import Path
from ase.calculators.vasp import Vasp
from .vasp_interactive import VaspInteractive

def main():
    """Running VaspInteractive as a socket client from command line.

    ASE's socket-I/O interface allows any DFT calculator that is compatible with the 
    iPI protol to communicate to a "socket server". In most common cases, a user may
    want to construct the socket server by the `SocketIOCalculator` class, and start 
    the client using `subprocess.Popen` method. This module provides a simple way of 
    launching a socket client using VaspInteractive by calling it from the command line.
    The implementation is also compatible with `ase.calculators.socketio.FileIOSocketClientLauncher`.

    Executing this module will start a VaspInteractive calculator on the current directory,
    and call the main loop calc.run(atoms) from there. The input parameters to start VaspInteractive
    will follow the order: 1) existing VASP input files 2) the parameter dumpfile `.vpi_param.pkl` 3)
    user provided json-format parameters via `--params` option.

    Usage:
        python -m vasp_interactive.socketio [parameters]

    Get help:
        python -m vasp_interactive.socketio -h
    """
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    workdir = Path(os.curdir).resolve()
    parser = ArgumentParser(usage=main.__doc__, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-p", "--port", help="Socket port", type=str, default="None")
    parser.add_argument("-sn", "--unixsocket", help="Unixsocket name", type=str, default="None")
    parser.add_argument("-ht", "--host", help="Hostname of socket sever", type=str, default="localhost")
    parser.add_argument(
        "--param-file", help="Parameter file", type=str, default=".vpi_param.pkl"
    )
    parser.add_argument(
        "--params", help="Additional parameters in json-format", type=str, default="{}"
    )
    args = parser.parse_args()
    port = args.port
    if port.lower() == "none":
        port = None
    else:
        try:
            port = int(port)
        except Exception as e:
            raise ValueError(f"Port value {port} is invalid") from e
    unixsocket = args.unixsocket
    if unixsocket.lower() == "none":
        unixsocket = None
    
    host = args.host
    if host.lower() == "none":
        host = None

    param_file = Path(args.param_file)
    if param_file.is_file():
        params = pickle.load(open(param_file, "rb"))
    else:
        params = {}

    user_inputs = json.loads(args.params)
    print(user_inputs)
    params.update(**user_inputs)

    # Use original Vasp restart to handle structure unfolding
    vc = Vasp(restart=True)
    atoms = vc.atoms
    # TODO: unpack parameters
    calc = VaspInteractive(
        # use_socket=args.socket, 
        use_socket=True,
        host=host,
        port=port, 
        unixsocket=unixsocket, 
        **params
    )
    with calc:
        calc.run(atoms)

if __name__ == "__main__":
    main()