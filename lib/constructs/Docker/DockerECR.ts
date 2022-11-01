import { Construct } from 'constructs'
import { Environment } from '../../stacks/environments'
import * as cdk from 'aws-cdk-lib';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as ecr_assets from 'aws-cdk-lib/aws-ecr-assets';
import * as path from 'path';
import * as fs from 'fs';

export interface DockerECRProps {
  /** Environment object */
  environment: Environment
  /** name of the group */
  name: String
}

export class DockerECR extends Construct {
    private props: DockerECRProps
    private dockerBucketName: string
    constructor(scope: Construct, id: string, props: DockerECRProps) {
      super(scope, id)
      this.props = props
      const directoryPath = path.join(__dirname, 'docker_images');
      fs.readdirSync(directoryPath).forEach(dockerFolder => {
        new ecr_assets.DockerImageAsset(this, dockerFolder, {
          directory: path.join(__dirname, 'docker_images/pyDockerBasicExample/'),
        })
      })
    }
}