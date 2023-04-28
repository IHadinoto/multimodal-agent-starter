"""Tool for generating images."""
import json
import logging

from langchain.agents import Tool
from steamship import Steamship
from steamship.base.error import SteamshipError
from steamship.data.plugin.plugin_instance import PluginInstance

NAME = "GenerateImage"

DESCRIPTION = """
Useful for when you need to generate an image. Provide a detailed text prompt for the desired image when invoking this
tool. Always include any UUIDs as part of the final answer returned to the user.
Output: the UUID of a generated image
"""

PLUGIN_HANDLE = "dall-e"


class GenerateImageTool(Tool):
    """Tool used to generate images from a text-prompt."""

    image_generator: PluginInstance

    def __init__(self, client: Steamship):

        super().__init__(
            name=NAME,
            func=self.run,
            description=DESCRIPTION,
            image_generator=client.use_plugin(
                plugin_handle=PLUGIN_HANDLE, config={"n": 1, "size": "256x256"}
            ),
        )

    def run(self, prompt: str, **kwargs) -> str:
        """Respond to LLM prompt."""
        logging.info(f"[{self.name}] {prompt}")
        if not isinstance(prompt, str):
            prompt = json.dumps(prompt)

        task = self.image_generator.generate(text=prompt, append_output_to_file=True)
        task.wait()
        blocks = task.output.blocks
        logging.info(f"[{self.name}] got back {len(blocks)} blocks")
        if len(blocks) > 0:
            logging.info(f"[{self.name}] image size: {len(blocks[0].raw())}")
            return blocks[0].id
        raise SteamshipError(f"[{self.name}] Tool unable to generate image!")
