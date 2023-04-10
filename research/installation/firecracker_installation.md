# Firecracker installation

## Prerequisites

### Architecture & OS

Firecracker supports **x86_64** and **aarch64** Linux, see
[specific supported kernels](kernel-policy.md).

### KVM

Firecracker requires [the KVM Linux kernel module](https://www.linux-kvm.org/).

The presence of the KVM module can be checked with:

```bash
lsmod | grep kvm
```

An example output where it is enabled:

```bash
kvm_intel             348160  0
kvm                   970752  1 kvm_intel
irqbypass              16384  1 kvm
```

### Docker

Firecracker uses docker image to install all dependencies.

## Installation

```bash
git clone https://github.com/firecracker-microvm/firecracker
cd firecracker
tools/devtool build
toolchain="$(uname -m)-unknown-linux-musl"
```
The Firecracker binary will be placed at
`build/cargo_target/${toolchain}/debug/firecracker`.
