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

However the command doesn't work with the last Containerd version. In order to fix this issue, correct release link was hardcoded. Corrected installation file presented [here](/kata/local/configuration/install.sh).

## Post-installation steps

Since the automatic installation script supports only first version of Containerd configuration files but installs Kata containers with the last  Containerd version, it is neccesary to change configuration file. Correct configuration file presented [here](/kata/local/configuration/containerd/config.toml). 

Restart containerd service

 ```bash
sudo systemctl restart containerd
```

## Test the installation

You are now ready to run Kata Containers. You can perform a simple test by
running the following commands:

```bash
image="docker.io/library/busybox:latest"
sudo ctr image pull "$image"
sudo ctr run --runtime "io.containerd.kata.v2" --rm -t "$image" test-kata uname -r
```

The last command above shows details of the kernel version running inside the
container, which will likely be different to the host kernel version. 
