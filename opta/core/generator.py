import os
from typing import Generator, List, Optional, Tuple

import yaml

from opta import gen_tf
from opta.blocks import Blocks
from opta.constants import TF_FILE_PATH
from opta.exceptions import UserErrors
from opta.layer import Layer
from opta.utils import deep_merge, logger


def gen_all(config: str, env: Optional[str], var: List[str] = []) -> None:
    # Just run the generator till the end
    list(gen(config, env, var))


def gen(
    config: str, env: Optional[str], var: List[str] = []
) -> Generator[Tuple[int, Blocks, int], None, None]:
    """ Generate TF file based on opta config file """
    if not os.path.exists(config):
        raise UserErrors(f"File {config} not found")

    conf = yaml.load(open(config), Loader=yaml.Loader)
    for v in var:
        key, value = v.split("=")
        conf["meta"]["variables"] = conf["meta"].get("variables", {})
        conf["meta"]["variables"][key] = value

    layer = Layer.load_from_dict(conf, env)
    logger.debug("Loading infra blocks")

    total_block_count = len(layer.blocks)
    for block_idx, block in enumerate(layer.blocks):
        logger.debug(f"Generating block {block_idx}")
        ret = layer.gen_providers(block_idx, block.backend_enabled)
        ret = deep_merge(layer.gen_tf(block_idx), ret)

        gen_tf.gen(ret, TF_FILE_PATH)

        yield (block_idx, block, total_block_count)