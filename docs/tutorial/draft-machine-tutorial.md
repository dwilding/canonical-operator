<!-- Sketch outline of tutorial (VERY WIP) -->

Set up a VM:

1. Install Multipass
2. `multipass launch --cpus 4 --memory 8G --disk 50G --name juju-lxd charm-dev`
3. `multipass shell juju-lxd`

```text
multipass launch --cpus 4 --memory 8G --disk 50G --name juju-lxd
...
sudo snap install --classic concierge
sudo concierge prepare -p machine
juju status  # verify that Juju is ready (model is called 'testing')
sudo snap install --classic astral-uv
uv tool update-shell
# restart shell
uv tool install tox --with tox-uv
```

From now on, work inside the VM.

```text
cd
mkdir tinyproxy-operator
cd tinyproxy-operator
charmcraft init --profile machine
charmcraft pack
# Packed tinyproxy-operator_amd64.charm
juju deploy ./tinyproxy-operator_amd64.charm
# Deploying "tinyproxy-operator" from local charm "tinyproxy-operator", revision 0 on ubuntu@22.04/stable
```

```text
$ juju status
Model    Controller     Cloud/Region         Version  SLA          Timestamp
testing  concierge-lxd  localhost/localhost  3.6.8    unsupported  08:01:07+01:00

App                 Version  Status  Scale  Charm               Channel  Rev  Exposed  Message
tinyproxy-operator           active      1  tinyproxy-operator             0  no

Unit                   Workload  Agent  Machine  Public address  Ports  Message
tinyproxy-operator/0*  active    idle   0        10.212.138.59

Machine  State    Address        Inst id        Base          AZ  Message
0        started  10.212.138.59  juju-e2a25d-0  ubuntu@22.04      Running
```

Modify charmcraft.yaml to add:

```yaml
charm-libs:
  - lib: operator_libs_linux.apt
    version: "0"
```

Run `charmcraft fetch-libs`.

In tinyproxy.py, import the lib and use it to install tinyproxy:

```py
from charms.operator_libs_linux.v0 import apt
def install() -> None:
    """Install the workload."""
    apt.update()
    apt.add_package("tinyproxy-bin")
    # TODO: Make sure to handle errors
    # See https://charmhub.io/operator-libs-linux/libraries/apt
```

Add `charmlibs-pathops` to deps in pyproject.toml.
Don't add it manually. Use `uv add` which removes the need to run `uv lock`.

Import pathops in tinyproxy.py:

```py
from charmlibs import pathops
```

On start, create the config file:

```py
def start() -> None:
    """Start the workload."""
    pathops.LocalPath("/etc/tinyproxy").mkdir(exist_ok=True)
    path = pathops.LocalPath("/etc/tinyproxy/tinyproxy.conf")
    path.write_text("""\
PidFile "/var/run/tinyproxy.pid"
Port 8888
Timeout 600
ReverseOnly Yes
ReversePath "/example/" "http://www.example.com/"
""")
    subprocess.run(["tinyproxy"], check=True)
```

Have a config option for the local URL path?

To ask tinyproxy to reload config, we can send `SIGUSR1`. Outside charm code:

```text
kill -USR1 1234
```

Where 1234 is the pid from /var/run/tinyproxy.pid
