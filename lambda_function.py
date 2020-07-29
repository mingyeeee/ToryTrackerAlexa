# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import boto3
from boto3.dynamodb.conditions import Key

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome, how can I help you? I can add, remove and search up items on the inventory list"
        reprompt_output = "I can help you add, remove and search up items on the inventory list"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_output)
                .response
        )

class QueryItemIntentHandler(AbstractRequestHandler):
    """Handler for queryItemIntent"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        # intents with 'if' do not work
        return ask_utils.is_intent_name("queryItemIntent")(handler_input)
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        itemToQuery = slots["item"].value
        
        #session token service api request
        sts_client = boto3.client('sts')
        assumed_role_object=sts_client.assume_role(RoleArn="arn:aws:iam::653314872953:role/alexaInventoryHelper-Policy", RoleSessionName="AssumeRoleSession1")
        credentials=assumed_role_object['Credentials']

        # 2. Make a new DynamoDB instance with the assumed role credentials
        dynamodb = boto3.resource('dynamodb',
                      aws_access_key_id=credentials['AccessKeyId'],
                      aws_secret_access_key=credentials['SecretAccessKey'],
                      aws_session_token=credentials['SessionToken'],
                      region_name='us-east-1')

        # 3. Perform DynamoDB operations on the table
        try:
            table = dynamodb.Table('InventoryHelper')
            response = table.query(
                KeyConditionExpression=Key('item').eq(itemToQuery)
            )
            if response['Count'] == 0:
                speak_output = "The item you requested was not found in the inventory list."
            else:
                response = table.get_item(Key={'item' : itemToQuery})
                totalQuantity = response['Item']['quantity']
                speak_output = "There are {totalQuantity} {itemToQuery} on the inventory list".format(totalQuantity = totalQuantity, itemToQuery = itemToQuery)

            # Use the response as required . .
        except ResourceNotExistsError:
        # Exception handling
            raise
        except Exception as e:
        # Exception handling
            raise e
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class RemoveItemIntentHandler(AbstractRequestHandler):
    """Handler for removeItemIntent"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("removeItemIntent")(handler_input)
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        itemToRemove = slots["item"].value
        quantityOfItem = slots["quantity"].value
        
        #session token service api request
        sts_client = boto3.client('sts')
        assumed_role_object=sts_client.assume_role(RoleArn="arn:aws:iam::653314872953:role/alexaInventoryHelper-Policy", RoleSessionName="AssumeRoleSession1")
        credentials=assumed_role_object['Credentials']

        # 2. Make a new DynamoDB instance with the assumed role credentials
        dynamodb = boto3.resource('dynamodb',
                      aws_access_key_id=credentials['AccessKeyId'],
                      aws_secret_access_key=credentials['SecretAccessKey'],
                      aws_session_token=credentials['SessionToken'],
                      region_name='us-east-1')

        # 3. Perform DynamoDB operations on the table
        try:
            table = dynamodb.Table('InventoryHelper')
            response = table.query(
                KeyConditionExpression=Key('item').eq(itemToRemove)
            )
            if response['Count'] == 0:
                speak_output = "The item you requested to remove was not found in the inventory list."
            else:
                response = table.get_item(Key={'item' : itemToRemove})
                totalQuantity = int(response['Item']['quantity']) - int(quantityOfItem)
                if totalQuantity < 0:
                    reportedQuantity = response['Item']['quantity']
                    speak_output = "Sorry, I cannot remove the requested quantity as there are only {reportedQuantity}".format(reportedQuantity = reportedQuantity)
                elif totalQuantity == 0:
                    speak_output = "I have removed {quantityOfItem}. There are 0 {itemToRemove} left.".format(quantityOfItem = quantityOfItem, itemToRemove = itemToRemove)
                    table.delete_item(Key={'item' : itemToRemove})
                else:
                    speak_output = "I have removed {quantityOfItem}. There are {totalQuantity} {itemToRemove} left.".format(quantityOfItem = quantityOfItem, totalQuantity = totalQuantity, itemToRemove = itemToRemove)
                    table.delete_item(Key={'item' : itemToRemove})
                    update = {"item" : itemToRemove, "quantity" : totalQuantity}
                    table.put_item(Item=update)

            # Use the response as required . .
        except ResourceNotExistsError:
        # Exception handling
            raise
        except Exception as e:
        # Exception handling
            raise e
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )
        
        
    
class AddItemIntentHandler(AbstractRequestHandler):
    """Handler for addItemIntent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("addItemIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        itemToAdd = slots["item"].value
        quantityOfItem = slots["quantity"].value
        
        #session token service api request
        sts_client = boto3.client('sts')
        assumed_role_object=sts_client.assume_role(RoleArn="arn:aws:iam::653314872953:role/alexaInventoryHelper-Policy", RoleSessionName="AssumeRoleSession1")
        credentials=assumed_role_object['Credentials']

        # 2. Make a new DynamoDB instance with the assumed role credentials
        dynamodb = boto3.resource('dynamodb',
                      aws_access_key_id=credentials['AccessKeyId'],
                      aws_secret_access_key=credentials['SecretAccessKey'],
                      aws_session_token=credentials['SessionToken'],
                      region_name='us-east-1')

        # 3. Perform DynamoDB operations on the table
        try:
            table = dynamodb.Table('InventoryHelper')
            response = table.query(
                KeyConditionExpression=Key('item').eq(itemToAdd)
            )
            if response['Count'] == 0:
                update = {"item" : slots["item"].value, "quantity" : slots["quantity"].value}
                table.put_item(Item=update)
                speak_output = "okay I have added {quantityOfItem} {itemToAdd}.".format(quantityOfItem = quantityOfItem, itemToAdd = itemToAdd)
            #else get item (quantity) then delete and update
            else:
                response = table.get_item(Key={'item' : itemToAdd})
                totalQuantity = int(quantityOfItem) + int(response['Item']['quantity'])
                speak_output = "okay, I have updated the inventory list. You have {totalQuantity} {itemToAdd} in total".format(totalQuantity=totalQuantity, itemToAdd=itemToAdd)
                #deletes item then repost an updated one
                table.delete_item(Key={'item' : itemToAdd})
                update = {"item" : itemToAdd, "quantity" : totalQuantity}
                table.put_item(Item=update)
            # Use the response as required . .
        except ResourceNotExistsError:
        # Exception handling
            raise
        except Exception as e:
        # Exception handling
            raise e

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AddItemIntentHandler())
sb.add_request_handler(RemoveItemIntentHandler())
sb.add_request_handler(QueryItemIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
