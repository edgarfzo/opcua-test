# Welcome to your CDK TypeScript project

This is a blank project for CDK development with TypeScript.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template




### Installation and creation of greengrass Thing and thing group

    Running the code ./scripts/gg_setup_ubuntu.sh for example in an ubuntu machine
    Need to create the Token Exchange Service (TES) provides credentials for Greengrass V2 Components running on the Greengrass Core so that the Components are able to access other AWS services. In this section you will create a role and an alias to the role that will define what AWS services your Components may access.

    Then create a role alias
# This project generates greengrass components from two main sources:
 # Lambda functions
 # Docker containers

 ## Lambda components:
    The lambda code lives in a folder under the file name index.py
    The dependencies should be pre installed in the Thing (to be improved)
    The runtime settings should match the index.lambda_handler of the functions
    The role of the lambda must allow interaction with the desired aws services and local gg services
    The role of the core device must also allow these interactions

    It should be possible to define the topics the lambda will be listening to like in:
     https://iot.awsworkshops.com/aws-greengrassv2/lab36-greengrassv2-components/

    The component should receive access to internal topics with the access conttrol in the merge config.
    This happends in the deployment

    For example: getting a component named com.cdk.opcua-trial to access iot core topic called ratchet-cloud
    Checked thay without this the component cant not use the iot core topic
{
  "accessControl": {
    "aws.greengrass.ipc.mqttproxy": {
      "com.cdk.opcua-trial:pubsub:1": {
        "policyDescription": "Allows access to publish to anything.",
        "operations": [
          "aws.greengrass#PublishToIoTCore"
        ],
        "resources": [
          "cloud-gg-topic"
        ]
      }
    }
  }
}



