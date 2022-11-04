import { Construct } from 'constructs'
import { Environment } from '../../stacks/environments'
import * as greengrassv2 from 'aws-cdk-lib/aws-greengrassv2';
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as python from '@aws-cdk/aws-lambda-python-alpha'
import * as cdk from 'aws-cdk-lib'
import * as iam from 'aws-cdk-lib/aws-iam'
import * as fs from 'fs';
// import * as s3 from "aws-cdk-lib/aws-s3";
import * as path from 'path';


export interface ggPythonLambdaComponentProps {
  /** Environment object */
  environment: Environment
  /** name of the group */
  name: String
}
export class ggPythonLambdaComponent extends Construct {
    private props: ggPythonLambdaComponentProps
    private lambdaFn: python.PythonFunction
    private lambdaArn: String
    constructor(scope: Construct, id: string, props: ggPythonLambdaComponentProps) {
      super(scope, id)
      this.props = props
      const directoryPath = path.join(__dirname, 'src');
      fs.readdirSync(directoryPath).forEach(lambdaFolder => {
        let lambdaConfigParams = require(path.join(__dirname, 'src/'+lambdaFolder+'/lambdaConfig.json'))
        this.createPythonLambda('function-'+ lambdaFolder , path.join(__dirname, 'src/'+lambdaFolder))
        this.createPythonLambdacomponent('com.cdk.'+ lambdaFolder, lambdaConfigParams["pinned"])
      })
    }
    /**
     * This function creates the core group 
     * @param props 
     */
    
    private createPythonLambda(name: string, filepath: string) {
         this.lambdaFn = new lambda.Function(this, name, {
          runtime: lambda.Runtime.PYTHON_3_8,
          timeout: cdk.Duration.seconds(60),
          handler: 'index.handler',
          code: lambda.Code.fromAsset(path.join(filepath, 'lambdaDeploy.zip')),
        });
          this.lambdaFn.addToRolePolicy(new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'iot:*',
            'glue:*',
            's3:*',
          ],
          resources: [
            '*',
          ],
        }))
         const version = this.lambdaFn.currentVersion
         console.log(version.functionArn)
         this.lambdaArn = this.lambdaFn.functionArn
      }
    private createPythonLambdacomponent(name: string, isPinned: boolean) {
      var vArn =  this.lambdaFn.currentVersion.version
      const lambdaFunctionLinuxProcessParams: greengrassv2.CfnComponentVersion.LambdaLinuxProcessParamsProperty = {
        isolationMode: 'NoContainer',
      }
      const lambdaFunctionExcecutionParams: greengrassv2.CfnComponentVersion.LambdaExecutionParametersProperty = {
        linuxProcessParams: lambdaFunctionLinuxProcessParams,
      }
      const lambdaFunctionRecipeSourceProperty: greengrassv2.CfnComponentVersion.LambdaFunctionRecipeSourceProperty = {
        lambdaArn: this.lambdaFn.currentVersion.functionArn,
        componentName: name,
        // https://docs.aws.amazon.com/cdk/v2/guide/tokens.html
        componentVersion: cdk.Lazy.string({
          produce() {
            return '1.0.' + vArn
          }
          }),
        componentLambdaParameters: {
          eventSources: [{
            topic: "local-data",
            type: "PUB_SUB"
          }],
          pinned: isPinned,
          linuxProcessParams: lambdaFunctionLinuxProcessParams,
          timeoutInSeconds: 60
        }
    }
    const ggComponent = new greengrassv2.CfnComponentVersion(this, name, {
      lambdaFunction: lambdaFunctionRecipeSourceProperty,
      
  });
  }
  
}