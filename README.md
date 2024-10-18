# LangGraph Tutorial using AWS Bedrock

This is the program created based on LangGraph tutorial.

## Environment

```bash
$ python -V
Python 3.12.5

$ pipenv --version
pipenv, version 2024.0.1
```

### Additional

- Enable LLM model in AWS Bedrock and keep the model ID
- Get API KEY of Tavily Search Engine

## How to setup

```bash
# install packages
pipenv install
# launch virtual env
pipenv shell
```

## How to run

```bash
export AWS_PROFILE=<your profile>
TAVILY_API_KEY=<your API key> python run_chatbot.py
```
