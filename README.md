# demo-repo
Reusable Artifacts to Create Demo's
## Prerequisites to setup this demo

In order to successfully complete this demo you need to install few tools before getting started.

- If you don't have a Confluent Cloud account, sign up for a free trial [here](https://www.confluent.io/confluent-cloud/tryfree).
- Install Confluent Cloud CLI by following the instructions [here](https://docs.confluent.io/confluent-cli/current/install.html).
- Please follow the instructions to install Terraform if it is not already installed on your system.[here](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)  
- This demo uses Python 3.9.13 version.
- This demo uses python modules. You can install this module through `pip`.
  ```
  pip3 install modulename
  ```

- Create Confluent Cloud API keys by following the steps in UI.Click on the button that is present on the right top section and click on Cloud API Key.
<div align="center"> 
  <img src="images/Cloud API Key.png" width =100% heigth=100%>
</div>
- Now Click Add Key to generate API keys and store it as we will be using that key in this demo.

- **Note:** This is different than Kafka cluster API keys.

## STEPS to deploy the demo

1. replace the values of the cloud api key and secret in variables.tf
2. Use below commands to setup kafka cluster and ksqldb cluster

 ```
  cd terraform
   ```
```
terraform init
```
```
terraform plan
```
```
terraform apply
```
3. Create topic named as **bank-transactions** and **customer-details** with 6 partitions.
4. Enable the Stream Governance Advance Package for the Environment
5. Create/Enable Tags [here](https://docs.confluent.io/cloud/current/stream-governance/stream-catalog.html#create-tags)
6. Create Business Metdata [here](https://docs.confluent.io/cloud/current/stream-governance/stream-catalog.html#examples)
7. Enter your bootstrap url, schema regitry url, cluster api key and secret, schema registry key and secret into the customer.py and tranasaction.py
8. Run producers using below commands


 ```
python3 transaction.py    
```
 ```
python3 customer.py
```
6. If you want to sink into s3 you can create s3 sink connector or into this demo the data of the final stream is getting sinked into topic **Customer-transactions**
