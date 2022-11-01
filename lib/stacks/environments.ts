export interface Environment {
    /** Id of the existing vpc in the account to use. */
    readonly name: string,
    readonly tags: {
      'Project': string,
      'Owner': string,
    }
    readonly awsEnv: {
      region: string,
      account: string,
    }
    }  
    
  
  interface Environments {
    /** An environment name (as string) that maps to environment configuration object.  */
    [name: string]: Environment
  }
  
  export const environments: Environments = {
    /** To create multiple environemtn configuration, create another key in the main object.*/
    'dev': {
      'name': 'dev',
      'tags': {
        Project: 'Greengrass',
        Owner: 'avgz'
      },
      'awsEnv': {
          account: '419458780298', // avgz personal
          region: 'eu-central-1',
        },
    },
  }