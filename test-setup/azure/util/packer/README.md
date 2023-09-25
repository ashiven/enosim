1. Download and install packer
2. create JSON files and configuration scripts for each image you want to build
3. run `packer build -var 'client_id=<your-client-id>' -var 'client_secret=<your-client-secret>' -var 'tenant_id=<your-tenant-id>' -var 'subscription_id=<your-subscription-id>' your-packer-template.json`
