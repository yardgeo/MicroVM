# Configure Kata Containers to use Firecracker

## Install Kata Containers

### KVM

MicroVMs require [the KVM Linux kernel module](https://www.linux-kvm.org/).

The presence of the KVM module can be checked with:

```bash
lsmod | grep kvm
```

An example output where it is enabled:

```bash
kvm_amd               147456  0
ccp                   106496  1 kvm_amd
kvm                   950272  1 kvm_amd
irqbypass              16384  1 kvm
```

### Install Kata containers

Get latest release
```bash
wget https://github.com/kata-containers/kata-containers/releases/download/3.0.2/kata-static-3.0.2-x86_64.tar.xz
sudo tar -xvf /home/vardgeo/kata-static-3.0.2-x86_64.tar.xz 
```
Kata Containers packages use a `/opt/kata/` prefix so either add that to
   your `PATH`, or create symbolic links for the following commands. The
   advantage of using symbolic links is that the `systemd(1)` configuration file
   for containerd will not need to be modified to allow the daemon to find this
   binary (see the [section on installing containerd](#install-containerd) below).

   | Command | Description |
   |-|-|
   | `/opt/kata/bin/containerd-shim-kata-v2` | The main Kata 2.x binary |
   | `/opt/kata/bin/kata-collect-data.sh`    | Data collection script used for [raising issues](https://github.com/kata-containers/kata-containers/issues) |
   | `/opt/kata/bin/kata-runtime`            | Utility command |
   
 Create symbolic links for the following commands
 ```bash
sudo ln -s /opt/kata/bin/kata-collect-data.sh /usr/local/bin/kata-collect-data.sh
sudo ln -s /opt/kata/bin/containerd-shim-kata-v2 /usr/local/bin/containerd-shim-kata-v2
sudo ln -s /opt/kata/bin/kata-runtime /usr/local/bin/kata-runtime
```

### Install containerd

Get latest release
```bash
wget https://github.com/containerd/containerd/releases/download/v1.7.0/containerd-1.7.0-linux-amd64.tar.gz
cd /usr/local/
sudo tar -xvf containerd-1.7.0-linux-amd64.tar.gz 
```
Configure containerd
Download the standard `systemd(1)` service file and install to
    `/etc/systemd/system/`
 ```bash
cd /lib/systemd/system/
sudo wget https://raw.githubusercontent.com/containerd/containerd/main/containerd.service
sudo systemctl daemon-reload
sudo systemctl enable containerd.service
sudo systemctl start containerd.service
```

Create containerd configuration file
 ```bash
sudo mkdir -p /etc/containerd
sudo containerd config default | sudo tee /etc/containerd/config.toml
sudo vi /etc/containerd/config.toml
```
Add the Kata Containers configuration to the containerd configuration file:

```toml
    [plugins]
      [plugins."io.containerd.grpc.v1.cri"]
        [plugins."io.containerd.grpc.v1.cri".containerd]
          default_runtime_name = "kata"
          [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]
            [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.kata]
              runtime_type = "io.containerd.kata.v2"
```
    
Restart containerd service
```bash
sudo systemctl restart containerd.service
```
## Install AWS Firecracker

Kata Containers only support AWS Firecracker v0.23.4 ([yet](https://github.com/kata-containers/kata-containers/pull/1519)).
To install Firecracker we need to get the `firecracker` and `jailer` binaries:

```bash
$ release_url="https://github.com/firecracker-microvm/firecracker/releases"
$ version="v0.23.1"
$ arch=`uname -m`
$ curl ${release_url}/download/${version}/firecracker-${version}-${arch} -o firecracker
$ curl ${release_url}/download/${version}/jailer-${version}-${arch} -o jailer
$ chmod +x jailer firecracker
```

To make the binaries available from the default system `PATH` it is recommended to move them to `/usr/local/bin` or add a symbolic link:

```bash
$ sudo ln -s $(pwd)/firecracker /usr/local/bin
$ sudo ln -s $(pwd)/jailer /usr/local/bin
```

In order to run Kata with AWS Firecracker a block device as the backing store for a VM is required. To interact with `containerd` and Kata we use the `devmapper` `snapshotter`.

## Configure `devmapper`
Based on a [very useful
guide](https://docs.docker.com/storage/storagedriver/device-mapper-driver/)
from docker, we can set it up using the following scripts:
```
#!/bin/bash
set -ex

DATA_DIR=/var/lib/containerd/devmapper
POOL_NAME=devpool

mkdir -p ${DATA_DIR}

# Create data file
sudo touch "${DATA_DIR}/data"
sudo truncate -s 100G "${DATA_DIR}/data"

# Create metadata file
sudo touch "${DATA_DIR}/meta"
sudo truncate -s 10G "${DATA_DIR}/meta"

# Allocate loop devices
DATA_DEV=$(sudo losetup --find --show "${DATA_DIR}/data")
META_DEV=$(sudo losetup --find --show "${DATA_DIR}/meta")

# Define thin-pool parameters.
# See https://www.kernel.org/doc/Documentation/device-mapper/thin-provisioning.txt for details.
SECTOR_SIZE=512
DATA_SIZE="$(sudo blockdev --getsize64 -q ${DATA_DEV})"
LENGTH_IN_SECTORS=$(bc <<< "${DATA_SIZE}/${SECTOR_SIZE}")
DATA_BLOCK_SIZE=128
LOW_WATER_MARK=32768

# Create a thin-pool device
sudo dmsetup create "${POOL_NAME}" \
    --table "0 ${LENGTH_IN_SECTORS} thin-pool ${META_DEV} ${DATA_DEV} ${DATA_BLOCK_SIZE} ${LOW_WATER_MARK}"

cat << EOF
#
# Add this to your config.toml configuration file and restart containerd daemon
#
[plugins]
  [plugins.devmapper]
    pool_name = "${POOL_NAME}"
    root_path = "${DATA_DIR}"
    base_image_size = "10GB"
    discard_blocks = true
EOF
```

Make it executable and run it:

```bash
$ sudo chmod +x scripts/devmapper/create.sh
$ cd scripts/devmapper/
$ sudo ./create.sh
```

Change containerd configuration:

```toml
[plugins]
  [plugins."io.containerd.snapshotter.v1.devmapper"]
    pool_name = "${POOL_NAME}"
    root_path = "${DATA_DIR}"
    base_image_size = "10GB"
    discard_blocks = true
```

```bash
sudo vi /etc/containerd/config.toml
sudo systemctl restart containerd
```

We can use `dmsetup` to verify that the thin-pool was created successfully.

```bash
$ sudo dmsetup ls
```

 We should also check that `devmapper` is registered and running:

```bash
$ sudo ctr plugins ls | grep devmapper
```

This script needs to be run only once, while setting up the `devmapper` `snapshotter` for `containerd`. Afterwards, make sure that on each reboot, the thin-pool is initialized from the same data directory. Otherwise, all the fetched containers (or the ones that you have created) will be re-initialized. A simple script that re-creates the thin-pool from the same data directory is shown below:

```
#!/bin/bash
set -ex

DATA_DIR=/var/lib/containerd/devmapper
POOL_NAME=devpool

# Allocate loop devices
DATA_DEV=$(sudo losetup --find --show "${DATA_DIR}/data")
META_DEV=$(sudo losetup --find --show "${DATA_DIR}/meta")

# Define thin-pool parameters.
# See https://www.kernel.org/doc/Documentation/device-mapper/thin-provisioning.txt for details.
SECTOR_SIZE=512
DATA_SIZE="$(sudo blockdev --getsize64 -q ${DATA_DEV})"
LENGTH_IN_SECTORS=$(bc <<< "${DATA_SIZE}/${SECTOR_SIZE}")
DATA_BLOCK_SIZE=128
LOW_WATER_MARK=32768

# Create a thin-pool device
sudo dmsetup create "${POOL_NAME}" \
    --table "0 ${LENGTH_IN_SECTORS} thin-pool ${META_DEV} ${DATA_DEV} ${DATA_BLOCK_SIZE} ${LOW_WATER_MARK}"
```

We can create a systemd service to run the above script on each reboot:

```bash
$ sudo nano /lib/systemd/system/devmapper_reload.service
```

The service file:

```
[Unit]
Description=Devmapper reload script

[Service]
ExecStart=/path/to/script/reload.sh

[Install]
WantedBy=multi-user.target
```

Enable the newly created service:

```bash
$ sudo systemctl daemon-reload
$ sudo systemctl enable devmapper_reload.service
$ sudo systemctl start devmapper_reload.service
```

