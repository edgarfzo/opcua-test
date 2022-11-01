import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Environment } from './environments'
import { ggPythonLambdaComponent } from '../constructs/lambda/component_lambda_basic';
import { DockerECR } from '../constructs/Docker/DockerECR';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export interface iotStackProps extends StackProps {
  /** The shared environemt variables for whole application */
  environment: Environment
}

export class iotStack extends Stack {
  
  constructor(scope: Construct, id: string, props: iotStackProps) {
    super(scope, id, props);
    /**
   * This function created the vpc object from the existing vpc in the account.
   * @param props Props from the stack
   */
    new DockerECR(this, 'avgz-iot-stack-ECR-Docker-Repository', {
      environment: props.environment,
      name: 'DockerStorageGG'
    })
    new ggPythonLambdaComponent(this, 'avgz-iot-stack-', {
      environment: props.environment,
      name: 'FirstIotBoxFunction'
    })
  }
  
}
