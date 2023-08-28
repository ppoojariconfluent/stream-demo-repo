#This part creates environment
resource "confluent_environment" "development" {
  display_name = "rti"
  }



#This part creates cluster inside environment
resource "confluent_kafka_cluster" "standard" {
  display_name = "rti-cluster"
  availability = "SINGLE_ZONE"
  cloud        = "AWS"
  region       = "us-east-2"
  standard {}

  environment {
    
  id=confluent_environment.development.id
  }

  }


##This part creates service account

resource "confluent_service_account" "rti_sa" {
  display_name = "rti_sa"
  description  = "terraform created"
}

##This part assigned role to the user  account created
resource "confluent_role_binding" "terraform_user-kafka-cluster-admin" {
  principal   = "User:${confluent_service_account.rti_sa.id}"
  role_name   = "CloudClusterAdmin"
  crn_pattern = confluent_kafka_cluster.standard.rbac_crn
}

# This part creates API Key for service account
resource "confluent_api_key" "clusterAPIKEY" {
  display_name = "clusterAPIKEY"
  description  = "Kafka API Key that is owned by 'terraform_user' service account"
  owner {
    id          = confluent_service_account.rti_sa.id
    api_version = confluent_service_account.rti_sa.api_version
    kind        = confluent_service_account.rti_sa.kind
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

resource "confluent_kafka_topic" "quote_requests" {
  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  topic_name    = "quote_requests"
  rest_endpoint      = confluent_kafka_cluster.standard.rest_endpoint
  credentials {
    key   = confluent_api_key.clusterAPIKEY.id
    secret = confluent_api_key.clusterAPIKEY.secret
  }
}

  
resource "confluent_ksql_cluster" "ksqldb" {
  display_name = "ksqldb-rti"
  csu          = 2

  kafka_cluster {
    id = confluent_kafka_cluster.standard.id
  }
  credential_identity {
    id = confluent_service_account.rti_sa.id
  }
  environment {
    id = confluent_environment.development.id
     
  }

}


