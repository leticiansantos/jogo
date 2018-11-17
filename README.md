# JoGo Media

Demo presented in SA Launch in Nov 17th 2018 in Irvine

JoGo Team:
- Zaid Altalib (altzaid@)
- Manish Sharma (sharmajt@)
- Sanjay Doiphode (sjdoi@)
- Ram Vittal (rvvittal@)
- Leticia dos Santos (sletic@)

## FYI

- You need to have an RDS instance created and update the connection information
chalicelib/db/models_mysql.py file
- The result image is being saved in the local file system. Not sure what happens
when it's running in the cloud
- For CodeCommit you need to configure your local repository origin. Once it's
done, each push to CodeCommit should trigger a deployment in the code pipeline
- To-do: Remove DynamoDB from project (we are not using anymore)

## Pre-requisites
- Python 3.6.5 (take a look at [`pyenv`](https://github.com/pyenv/pyenv))
- virtualenv and virtualenvwrapper

## How to run locally

- Clone this repo
- Create a Python 3.6.5 virtual env: `mkvirtualenv jogo --python=python3.6.5`
- Install dependencies: `pip install -r src/requirements-dev.txt`
- Install Local DynamoDB: `sudo make install-ddb -C src/`
- Start local DynamoDB instance: `make start-ddb -C src/`
- Start local app server: `make run -C src/`
- To deploy it to your aws account: `make deploy-test -C src/`

You can access using `http://localhost:8000`


## CI/CD pipeline

### Create CloudFormation stack

```
aws cloudformation deploy --stack-name jogo --template-file pipeline.yaml --capabilities CAPABILITY_IAM
```

### Setup CodeCommit integration

Use the CodeCommit endpoint provided by the CloudFormation stack output.

```
git remote add codecommit [codecommit-url]
```
