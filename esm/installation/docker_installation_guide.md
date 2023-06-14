#  ESM docker installation guide

## Prerequirements

GPU available

## Install dependencies 

[Evolutionary Scale Modeling (ESM)](https://github.com/facebookresearch/esm) requires nvcc and (openfold)[https://github.com/aqlaboratory/openfold] to be installed.

1.  Install [Docker](https://www.docker.com/).
    *   Install
        [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
        for GPU support.
    *   Setup running
        [Docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).
        
2.  Clone the openfold repository and `cd` into it.

    ```bash
    git clone https://github.com/aqlaboratory/openfold.git
    cd openfold
    ```
3.  Add esm dependencies to the environment.yml file. You can find example of enviroment file which was tested [here](./environment.yml)
4.  Building the docker image

```bash
docker build -t openfold .
```
5. Now you can use openfold image to run esm using pypi esm lybrary with the following command:
```bash
docker run --gpus all -it --rm \
-v /home/ubuntu/esm/esm/test_script:/opt/openfold/test_script \ # path to test scripts
-v /mnt/alphafold/input/esm/checkpoints:/root/.cache/torch/hub/checkpoints \ # path to models
openfold python test_script/test.py
```
6. Pypi esm lybrary uses torch and download all models to /root/.cache/torch/hub/checkpoints filepath. In order to not download models every container runtime it is recommended to mount it.
7. [Official esm guide](https://github.com/facebookresearch/esm)  suggests to use esmfold_v1 from pretrained models dataset.
 Although this model is recommended it requires a lot of resources (RAM and CPU). To verify esm installation esmfold_structure_module_only_8M was used.
8. You can find test script [here](./test.py).
