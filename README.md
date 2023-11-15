[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/ashiven/enosimulator/actions/workflows/tests.yml/badge.svg)](https://github.com/ashiven/enosimulator/actions/workflows/tests.yml)
[![PyPI version](https://badge.fury.io/py/enosimulator.svg)](https://badge.fury.io/py/enosimulator)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white)
![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)

## About

This software can be used to simulate an attack/defense cybersecurity competition using the game engine and services provided by [Enowars](https://github.com/enowars). For further information on how to use it, please refer to the [documentation](docs/README.md).

## Getting Started

### Prerequisites

-  Download and install the latest versions of [Python](https://www.python.org/downloads/) and [Pip](https://pypi.org/project/pip/).
-  Download and install the latest version of [Terraform](https://developer.hashicorp.com/terraform/downloads?product_intent=terraform).
-  Download and install the latest version of [Packer](https://www.packer.io/downloads).
-  Create an account with your preferred cloud provider (currently supporting [Microsoft Azure](https://azure.microsoft.com/en-us) and [Hetzner Cloud](https://www.hetzner.com/cloud)).
-  If you are using Windows, make sure to install [Git Bash](https://gitforwindows.org/) and add `C:\Program Files\Git\bin` to your **PATH** environment variable to be able to run shell scripts.

### Setup

#### Pip

1. Install the package via pip:

   ```bash
   pip install --user enosimulator
   ```

2. Start the simulation with the following command:

   ```bash
   enosimulator -c /path/to/config.json -s /path/to/secrets.json -v
   ```

#### Manual

1. Clone the repository to your local machine as follows:

   ```bash
   git clone https://github.com/ashiven/enosimulator.git
   ```

2. Install the necessary dependencies:

   ```bash
   pip install --user -r requirements.txt
   ```

3. Start the program (paths to the configuration files can also be defined in the environment variables `ENOSIMULATOR_CONFIG` and `ENOSIMULATOR_SECRETS`):

   ```bash
   python enosimulator -c /path/to/config.json -s /path/to/secrets.json
   ```

4. Navigate to the frontend directory and start the frontend:

   ```bash
   cd ./frontend && npm install && npm run build && npm run start
   ```

5. A graphical user interface is available at `http://localhost:3000` to monitor the simulation. (It may take up to 20 minutes for the simulation to start.)

#### Docker

1. Clone the repository to your local machine as follows:

   ```bash
   git clone https://github.com/ashiven/enosimulator.git
   ```

2. Create an SSH key pair in the **config** directory:

   ```bash
   ssh-keygen -f ./enosimulator/config/simkey
   ```

3. Specify simulation details in **enosimulator/config/config.json** and **enosimulator/config/secrets.json** with the following SSH key paths.

   ```json
   {
      "vm-secrets": {
         "ssh-public-key-path": "/app/enosimulator/config/simkey.pub",
         "ssh-private-key-path": "/app/enosimulator/config/simkey"
      }
   }
   ```

   ```json
   {
      "setup": {
         "ssh-config-path": "/app/enosimulator/config/simconfig"
      }
   }
   ```

4. Start the docker containers:

   ```bash
   docker compose up -d
   ```

5. A graphical user interface is available at `http://localhost:3000` to monitor the simulation. (It may take up to 20 minutes for the simulation to start.)

### Configuration

There are two configuration files that need to be supplied before launching the simulation (examples can be found [here](/enosimulator/config/examples)).

#### secrets.json

```json
{
   "vm-secrets": {
      "github-personal-access-token": "<string> <required> <a github personal access token that will be used on machines to pull repositories>",
      "ssh-public-key-path": "<string> <required> <path to the public key that will be stored on machines>",
      "ssh-private-key-path": "<string> <required> <path to the matching private key that will be used to connect to machines>"
   },
   "cloud-secrets": {
      "azure-service-principal": {
         "subscription-id": "<string> <required> <the azure subscription id>",
         "client-id": "<string> <required> <the azure service principal client id>",
         "client-secret": "<string> <required> <the azure service principal client secret>",
         "tenant-id": "<string> <required> <the azure service principal tenant id>"
      },
      "hetzner-api-token": "<string> <required> <the hetzner api token>"
   }
}
```

#### config.json

```json
{
   "setup": {
      "ssh-config-path": "<string> <required> <the path, including filename, where the ssh config for the simulation should be saved locally>",
      "location": "<string> <required> <'local' or the name of the cloud provider to be used for the simulation setup>",
      "vm-sizes": {
         "vulnbox": "<string> <required> <the size of the vms that should be used for the vulnboxes>",
         "checker": "<string> <required> <the size of the vms that should be used for the checkers>",
         "engine": "<string> <required> <the size of the vms that should be used for the engine>"
      },
      "vm-image-references": {
         "vulnbox": "<string> <optional> <a vm image that should be used for vulnboxes>",
         "checker": "<string> <optional> <a vm image that should be used for checkers>",
         "engine": "<string> <optional> <a vm image that should be used for the engine>"
      }
   },
   "settings": {
      "duration-in-minutes": "<int> <required> <the duration of the simulation in minutes>",
      "teams": "<int> <required> <the number of teams that should participate in the simulation>",
      "services": "<List(string)> <required> <the repository names of the services that should be used for the simulation>",
      "checker-ports": "<List(int)> <required> <the port numbers of the service checkers. the order should be the same as in services>",
      "simulation-type": "<string> <required> <the type of simulation to run. choose between 'realistic', 'basic-stress-test', 'stress-test' and 'intensive-stress-test'>",
      "scoreboard-file": "<string> <optional> <the path to a scoreboard file in json format from a past competition that will be used to derive a team experience distribution for the simulation>"
   },
   "ctf-json": {
      "title": "<string> <required> <the title of the ctf>",
      "flag-validity-in-rounds": "<int> <required> <the number of rounds a flag is valid>",
      "checked-rounds-per-round": "<int> <required> <the number of rounds checked per round>",
      "round-length-in-seconds": "<int> <required> <the length of a round in seconds>"
   }
}
```

### Packer Images

The deployment process can be sped up considerably by using virtual machine images that were created with [Packer](https://www.packer.io/). The following steps describe how to create such images.

1. Navigate to the **packer** directory for your chosen cloud provider. For example, for Hetzner Cloud:

   ```bash
   cd ./packer/hetzner
   ```

2. Install the Hetzner plugin for Packer:

   ```bash
   packer plugins install github.com/hashicorp/hcloud
   ```

3. Modify the available provisioning scripts and build templates to your liking. For example, you can add the specific services to be played during the simulation.

4. Make sure to also add your [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) to the provisioning script so it can be used to pull repositories from GitHub. For this, modify the following line in the provisioning script:

   ```bash
   pat="<insert-your-token-here>"
   ```

5. Build the image:

   ```bash
   packer build -var 'hcloud_token=<insert-your-token-here>' your-packer-template.json
   ```

## Monitoring

### Browser UI

There is a browser UI available at `http://localhost:3000` that can be used to monitor the simulation.

![frontend1](https://raw.githubusercontent.com/ashiven/enosimulator/main/docs/img/Frontend1.PNG)

![frontend2](https://raw.githubusercontent.com/ashiven/enosimulator/main/docs/img/Frontend2.PNG)

### CLI

To receive detailed information about the current state of the simulation in the CLI, start the program with the `-v` flag. The following command should be used:

```bash
python enosimulator -c /path/to/config.json -s /path/to/secrets.json -v
```

![cli1](https://raw.githubusercontent.com/ashiven/enosimulator/main/docs/img/CLI1.PNG)

![cli2](https://raw.githubusercontent.com/ashiven/enosimulator/main/docs/img/CLI2.PNG)

![cli3](https://raw.githubusercontent.com/ashiven/enosimulator/main/docs/img/CLI3.PNG)

### Scoreboard

The current state of the scoreboard can be monitored via the public IP address of the engine VM. It is available at `http://<engine-ip>:5001/scoreboard`.

![scoreboard1](https://raw.githubusercontent.com/ashiven/enosimulator/main/docs/img/Scoreboard1.PNG)

### Direct connections via SSH

During the process of building the simulation infrastructure, an SSH configuration file will be generated in the location specified inside **config.json**. To connect to a specific VM via SSH, use the following command:

```bash
ssh -F /path/to/simconfig <vm-name>
```

---

> GitHub [@ashiven](https://github.com/Ashiven) &nbsp;&middot;&nbsp;
> Twitter [ashiven\_](https://twitter.com/ashiven_)
