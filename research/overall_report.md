# Overall report



## MicroVms Test run

```bash

image="docker.io/library/busybox:latest"

sudo ctr image pull "$image"

sudo ctr run --runtime "io.containerd.kata.v2" --rm -t "$image" test-kata uname -r

```



The last command above shows details of the kernel version running inside the

container, which will likely be different to the host kernel version.



## How to run a custom image



Kata does not provide a mechanism to build a container image, but supports container images which were built using Docker, Podman or rkt.

For instance, it is possible to pull and run a custom image from DockerHub repository which was built using Dockerfile (tested on the bare metal machine).



### Running bioinformatics application



```bash

image="docker.io/biocontainers/blast:2.2.31"

sudo ctr image pull "$image"

sudo ctr run --runtime "io.containerd.kata.v2" --mount "type=bind,src=$PWD/host-data/,dst=/data/,options=rbind" --rm -t "$image" test-blastd blastp -query P04156.fasta -db zebrafish.1.protein.faa -out results2.txt

```



### Building local container



[nerdctl](https://github.com/containerd/nerdctl) is a Docker-compatible CLI for containerd.



#### Install

```bash

wget https://github.com/containerd/nerdctl/releases/download/v1.3.1/nerdctl-1.3.1-linux-amd64.tar.gz

tar -xvf nerdctl-1.3.1-linux-amd64.tar.gz 

sudo ln -s `pwd`/nerdctl /usr/local/bin

```



#### Run

```bash

nerdctl build -t foo /some-dockerfile-directory

nerdctl run -it --rm foo

```



## MicroVm limitations



General limitations are described [here](https://github.com/kata-containers/kata-containers/blob/main/docs/Limitations.md).



### Hypervisors

The hypervisor specified in the configuration file creates a VM to host the agent and the workload inside the container environment.

[List of all supported hypervisors](https://github.com/kata-containers/kata-containers/blob/main/docs/hypervisors.md)



### GPU support



In theory, Kata containers technology supports GPUs for container runtime, but I can't test it on the bare metal machine.

[Guide](https://github.com/kata-containers/kata-containers/blob/main/docs/use-cases/GPU-passthrough-and-Kata.md)



### Kubernetes support



It is possible to run a container image(pod) in kubernetes using Kata runtime (=microvm).

[Guide](https://github.com/kata-containers/kata-containers/blob/main/docs/how-to/how-to-use-k8s-with-containerd-and-kata.md)









## Comparing MicroVm to Docker



### Performance



1. Docker stats command can be used to estimate CPU and RAM for docker.

2. There are no analogs for docker stats command for MicroVm, so 3 party application integration is required.



### Isolation



1. Multiple containers share environmental variables if and only if they are explicitly linked (-- link arg) which is deprecated arg. [Source](https://docs.docker.com/network/links/)
<img width="682" alt="image" src="https://user-images.githubusercontent.com/43379766/235499012-d5f3152c-22e8-4883-909c-ef98543179f1.png">

2. MicroVm provides strong container isolation and sharing environmental variables is not possible.

