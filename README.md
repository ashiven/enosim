[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## About

This software can be used to simulate an attack/defense cybersecurity competition using the game engine and services provided by [Enowars](https://github.com/enowars). For further information on how to use it, please refer to the [documentation](docs/README.md).

## Getting Started

### Prerequisites

-  Download and install the latest versions of [Python](https://www.python.org/downloads/) and [Pip](https://pypi.org/project/pip/).
-  Download and install the latest version of [Terraform](https://developer.hashicorp.com/terraform/downloads?product_intent=terraform).
-  Download and install the latest version of [Packer](https://www.packer.io/downloads).
-  Create an account with your preferred cloud provider (currently supporting [Microsoft Azure](https://azure.microsoft.com/en-us) and [Hetzner Cloud](https://www.hetzner.com/cloud)).

### Setup

1. Clone the repository to your local machine as follows:

   ```bash
   git clone https://github.com/ashiven/enosimulator.git
   ```

2. Install the necessary dependencies:

   ```bash
   pip install --user -r requirements.txt
   ```

3. Specify simulation details in **config.json** and **secrets.json**.

4. Start the program:

   ```bash
   python enosimulator -c /path/to/config.json -s /path/to/secrets.json
   ```

### Configuration

There are two configuration files that need to be supplied before launching the simulation (examples can be found [here](/config/examples)).

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
      "vm-size": "<string> <required> <the size of the vms that should be used for the simulation setup>",
      "vm-image-references": {
         "vulnbox": "<string> <optional> <a vm image that should be used for vulnboxes>",
         "checker": "<string> <optional> <a vm image that should be used for checkers>",
         "engine": "<string> <optional> <a vm image that should be used for the engine>"
      }
   },
   "settings": {
      "duration-in-minutes": "<int> <required> <the duration of the simulation in minutes>",
      "teams": "<int> <required> <the number of teams that should participate in the simulation>",
      "vulnboxes": "<int> <required> <the number of vulnboxes that should be used for the simulation>",
      "services": "<List(string)> <required> <the repository names of the services that should be used for the simulation>",
      "checker-ports": "<List(int)> <required> <the port numbers of the service checkers. the order should be the same as in services>",
      "simulation-type": "<string> <required> <the type of simulation to run. choose between 'realistic' and 'stress-test'>"
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
   cd test-setup/hetzner/util/packer
   ```

2. Install the Hetzner plugin for Packer:

   ```bash
   packer plugins install github.com/hashicorp/hcloud
   ```

3. Modify the available provisioning scripts and build templates to your liking. For example, you can add the specific services to be played during the simulation.

4. Build the image:

   ```bash
   packer build your-packer-template.json
   ```

## Monitoring

### Browser UI

### CLI

### EnoScoreboard

### Direct connections via SSH

---

> GitHub [@ashiven](https://github.com/Ashiven) &nbsp;&middot;&nbsp;
> Twitter [ashiven\_](https://twitter.com/ashiven_)
