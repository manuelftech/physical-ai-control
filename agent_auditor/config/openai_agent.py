from config.config_vars import config
from openai import OpenAI
from agents import Agent, AgentOutputSchema, Runner
import structlog
logger = structlog.get_logger()

class OpenAIAgent():
    _singleton = None
    _is_already_initialized = False

    def __init__(self):
        if not self._is_already_initialized:
            self.runner = self._get_runner()
            self._is_already_initialized = True

    def _get_runner(self):
        logger.info("Connecting to OpenAI")
        runner = Runner()
        try:
            runner.run_sync(
                starting_agent=Agent(name="SystemCheck", model=config.LLM_MODEL),
                input="Confirm connectivity",
                max_turns=1
            )
        except Exception as e:
            logger.info("Error connecting to OpenAI")
            raise Exception(e)
        logger.info("Connected to OpenAI")
        return runner
    
    async def run_agent(self, name, instructions=None, output_type=None):
        agent = Agent(name=name, model=config.LLM_MODEL)
        if output_type:
            agent.output_type=AgentOutputSchema(output_type, strict_json_schema=True)
        return await self.runner.run(agent, input=instructions)
    
    def __new__(cls):
        if cls._singleton is None:
            cls._singleton = super(OpenAIAgent, cls).__new__(cls)
        return cls._singleton