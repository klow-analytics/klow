import apache_beam as beam
import logging

from user_agents import parse
from ...utils.helper import deep_get


class DeviceEnrichmentFn(beam.DoFn):
    def _get_device_category(self, user_agent):
        if user_agent.is_mobile:
            return "Mobile"

        if user_agent.is_tablet:
            return "Tablet"

        if user_agent.is_pc:
            return "Desktop"

        if user_agent.is_bot:
            return "Bot"

        return "Other"

    def process(self, element):
        try:
            user_agent_str = deep_get(element, "header", "userAgent")
            user_agent = parse(user_agent_str)

            element["device"] = element.get("device", {})

            element["device"]["browser"] = user_agent.browser.family
            element["device"]["browserVersion"] = user_agent.browser.version_string
            element["device"]["deviceCategory"] = self._get_device_category(user_agent)
            element["device"]["operatingSystem"] = user_agent.os.family
            element["device"]["operatingSystemVersion"] = user_agent.os.version_string

            if user_agent.is_mobile:
                element["device"]["mobileDeviceMarketingName"] = user_agent.device.family
                element["device"]["mobileDeviceModel"] = user_agent.device.model
                element["device"]["mobileDeviceBranding"] = user_agent.device.brand

            element["device"]["browserSize"] = deep_get(element, "systemInfo", "viewportSize")
            element["device"]["screenResolution"] = deep_get(element, "systemInfo", "screenResolution")

            yield element
        except Exception as e:
            logging.exception(e)
            yield element
