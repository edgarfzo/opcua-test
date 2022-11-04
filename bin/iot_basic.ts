#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { iotStack } from '../lib/stacks/iot_stack';
import { environments } from '../lib/stacks/environments'
const app = new cdk.App();

const environment = environments.dev

new iotStack(app, 'IotStack', {
  env: environment.awsEnv,
  environment: environment
});
