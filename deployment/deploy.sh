#!/bin/bash

printf "\nBegin Deployment of GCP Function.\n"

function finish {
    rv=$?
    printf "\nDeployment completed with code ${rv}\n"
}

trap finish EXIT

current_directory=$(dirname $0)
pushd ${current_directory}

set -e

echo "Initialising Terraform."
terraform init

echo "Planning Terraform."
terraform plan \
    -out=output.tfplan

echo "Applying Terraform."
terraform apply \
    -auto-approve \
    "output.tfplan"
