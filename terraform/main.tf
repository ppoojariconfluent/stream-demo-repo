#This part creates environment
resource "confluent_environment" "development" {
  display_name = "demo-env"
  }



#This part creates cluster inside environment
resource "confluent_kafka_cluster" "standard" {
  display_name = "demo-cluster"
  availability = "SINGLE_ZONE"
  cloud        = "AWS"
  region       = "us-east-2"
  standard {}

  environment {
    
  id=confluent_environment.development.id
  }

  }


##This part creates service account

resource "confluent_service_account" "demo_sa" {
  display_name = "demo_sa"
  description  = "terraform created"
}

##This part assigned role to the user  account created
resource "confluent_role_binding" "terraform_user-kafka-cluster-admin" {
  principal   = "User:${confluent_service_account.demo_sa.id}"
  role_name   = "CloudClusterAdmin"
  crn_pattern = confluent_kafka_cluster.standard.rbac_crn
}

# This part creates API Key for service account
resource "confluent_api_key" "clusterAPIKEY" {
  display_name = "clusterAPIKEY"
  description  = "Kafka API Key that is owned by 'terraform_user' service account"
  owner {
    id          = confluent_service_account.demo_sa.id
    api_version = confluent_service_account.demo_sa.api_version
    kind        = confluent_service_account.demo_sa.kind
  }

  managed_resource {
    id          = confluent_kafka_cluster.standard.id
    api_version = confluent_kafka_cluster.standard.api_version
    kind        = confluent_kafka_cluster.standard.kind

    environment {
     id = confluent_environment.development.id
     
    }
  }

}
   

# This part creates a topic 

resource "confluent_kafka_topic" "bank-transactions" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  topic_name    = "bank-transactions"
  rest_endpoint      = confluent_kafka_cluster.standard.rest_endpoint
  credentials {
    key   = confluent_api_key.clusterAPIKEY.id
    secret = confluent_api_key.clusterAPIKEY.secret
  }
}

resource "confluent_kafka_topic" "customer-details" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  topic_name    = "customer-details"
  rest_endpoint      = confluent_kafka_cluster.standard.rest_endpoint
  credentials {
    key   = confluent_api_key.clusterAPIKEY.id
    secret = confluent_api_key.clusterAPIKEY.secret
  }
}

  
resource "confluent_ksql_cluster" "ksqldb" {
  display_name = "ksqldb-demo"
  csu          = 2

  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  credential_identity {
    id = confluent_service_account.demo_sa.id
  }
  environment {
    id = confluent_environment.development.id
     
  }

}


