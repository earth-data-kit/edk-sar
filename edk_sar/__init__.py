import edk_sar.workflows
import edk_sar.frameworks
import edk_sar.xarray_accessor
import edk_sar.constants

import logging
import os
from osgeo import gdal

gdal.UseExceptions()

logger = logging.getLogger(__name__)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

logging.basicConfig(level=LOG_LEVEL)

logging.addLevelName(logging.INFO, "info")
logging.addLevelName(logging.ERROR, "error")
logging.addLevelName(logging.DEBUG, "debug")
logging.addLevelName(logging.WARNING, "warning")
logging.addLevelName(logging.CRITICAL, "critical")


logging.getLogger().handlers.clear()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[%(asctime)s] - [%(name)s:%(lineno)d] - [%(levelname)s] - %(message)s"
)

handler.setFormatter(formatter)
logger.addHandler(handler)


def init(env_path):
    edk_sar.frameworks.isce2.init(env_path)
