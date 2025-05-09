import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation, pins
from esphome.components import display, spi
from esphome.const import (
    CONF_BUSY_PIN,
    CONF_ID,
    CONF_LAMBDA,
    CONF_NAME,
    CONF_PAGES,
    CONF_RESET_PIN,
    CONF_REVERSED,
)

DEPENDENCIES = ["spi"]

CONF_DISPLAY_CS_PIN = "display_cs_pin"

it8951e_ns = cg.esphome_ns.namespace("it8951e")
IT8951EDisplay = it8951e_ns.class_(
    "IT8951EDisplay", cg.PollingComponent, spi.SPIDevice, display.DisplayBuffer
)
ClearAction = it8951e_ns.class_("ClearAction", automation.Action)

CONFIG_SCHEMA = cv.All(
    display.FULL_DISPLAY_SCHEMA.extend(
        {
            cv.GenerateID(): cv.declare_id(IT8951EDisplay),
            cv.Optional(CONF_NAME): cv.string,
            cv.Required(CONF_RESET_PIN): pins.gpio_output_pin_schema,
            cv.Required(CONF_BUSY_PIN): pins.gpio_input_pin_schema,
            cv.Optional(CONF_REVERSED): cv.boolean,
        }
    )
    .extend(cv.polling_component_schema("30s"))
    .extend(spi.spi_device_schema(cs_pin_required=True)),
    cv.has_at_most_one_key(CONF_PAGES, CONF_LAMBDA),
)


@automation.register_action(
    "it8951e.clear",
    ClearAction,
    automation.maybe_simple_id(
        {
            cv.GenerateID(): cv.use_id(IT8951EDisplay),
        }
    ),
)
async def it8951e_clear_to_code(config, action_id, template_arg, args):
    var = cg.new_Pvariable(action_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])
    return var


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await display.register_display(var, config)
    await cg.register_component(var, config)
    await spi.register_spi_device(var, config)

    if CONF_LAMBDA in config:
        lambda_ = await cg.process_lambda(
            config[CONF_LAMBDA], [(display.DisplayBufferRef, "it")], return_type=cg.void
        )
        cg.add(var.set_writer(lambda_))
    if CONF_RESET_PIN in config:
        reset = await cg.gpio_pin_expression(config[CONF_RESET_PIN])
        cg.add(var.set_reset_pin(reset))
    if CONF_BUSY_PIN in config:
        busy = await cg.gpio_pin_expression(config[CONF_BUSY_PIN])
        cg.add(var.set_busy_pin(busy))
    if CONF_REVERSED in config:
        cg.add(var.set_reversed(config[CONF_REVERSED]))
