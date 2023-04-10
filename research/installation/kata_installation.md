# Install Kata containers

## Prerequisites

Kata Containers requires nested virtualization or bare metal. Check 
[hardware requirements](https://github.com/kata-containers/kata-containers/blob/main/src/runtime/README.md#hardware-requirements) to see if your system is capable of running Kata 
Containers.

## Automatic Installation

[Automatic installation](https://github.com/kata-containers/kata-containers/blob/main/utils/README.md) method was used. 

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/kata-containers/kata-containers/main/utils/kata-manager.sh)"
```

However the command doesn't work with the last Containerd version. In order to fix this issue, correct release link was hardcoded. Corrected installation file presented here.

## Post-installation steps

Since the automatic installation script supports only first version of Kata containers configuration but installs Kata containers 2.0, it is neccesary to change configuration file. Correct configuration file presented here. 
 
