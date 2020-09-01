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

def findKeysandTable(fooditem):
    beefKeywords = {"meat","steak","liver","shepherd","veal","beef","traditional","bolognese"}
    poultryKeywords = {"chicken","turkey"}
    porkKeywords = {"pork","tourtiere","ham","bangers"}
    fishKeywords = {"fish","tuna","salmon"}
    dessertKeywords = {"mousse","tart","shortcake","cheesecake","cake","crisp","cobbler","pudding","cocktail","brownie","streusel"}
    
    if "thicken" in fooditem:
        SecondaryItemKey = {'broccoli','carrot','cauliflower','chicken','mushroom','tomato'}
        for sortKeys in SecondaryItemKey:
            if sortKeys in fooditem:
                return "ThickenedSoupTable","thickened",sortKeys
    if "soup" in fooditem:
        SecondaryItemKey = {'barley','cauliflower','turkey','tomato','beef','carrot','mushroom','pea','potato','broccoli','country','chicken and vegetable','squash','lentil','minestrone','noodle'}
        for sortKeys in SecondaryItemKey:
            if sortKeys in fooditem:
                return "SoupTable","soup",sortKeys
    if "pureed" in fooditem:
        SecondaryItemKey = {'king','lasadna','apple','cheese','pie','turkey dinner','beef vegetable','roast','sweet','meatloaf','lemon','cacciatore','spaghetti','turkey casserole','salmon','fruit'}
        for sortKeys in SecondaryItemKey:
            if sortKeys in fooditem:
                return "PureedTable","pureed",sortKeys
    if "minced" in fooditem:
        SecondaryItemKey = {'beef','apple','ham','king','turkey','pesto','pasta','stew','honey','vegetarian','pork'}
        for sortKeys in SecondaryItemKey:
            if sortKeys in fooditem:
                return "MincedTable",'minceed',sortKeys
    for x in poultryKeywords:
        if x in fooditem:
            SecondaryItemKey = {'king','country','breaded chicken breast','cacciatore','thigh','lemon','breaded chicken fingers','general','stew','white','chili','pie','sweet','bacon','mushroom','honey','penne','curry','ranch','stuffing','tangy','hawaiian','gravy'}
            for sortKeys in SecondaryItemKey:
                if sortKeys in fooditem:
                    return "PoultryTable",x,sortKeys
    for x in porkKeywords:
        if x in fooditem:
            SecondaryItemKey = {'stuffing','pie','rib','baked','mash','seasoned','apple braised','apple pork'}
            for sortKeys in SecondaryItemKey:
                if sortKeys in fooditem:
                    return "PorkTable",x,sortKeys
    for x in fishKeywords:
        if x in fooditem:
            SecondaryItemKey = {'florentine','chips','casserole','lemon','asian','cakes','herbed'}
            for sortKeys in SecondaryItemKey:
                if sortKeys in fooditem:
                    return "FishTable",x,sortKeys
    for x in beefKeywords:
        if x in fooditem:
            SecondaryItemKey = {'casserole','stew','salisbury','pie','chopped','mushroom','in gravy','stroganoff','onion','peppers','mushroom','stew','roast','casserole','roast'}
            for sortKeys in SecondaryItemKey:
                if sortKeys in fooditem:
                    return "BeefTable",x,sortKeys
    for x in dessertKeywords:
        if x in fooditem:
            SecondaryItemKey = {'chocolate','strawberry','tangerine','butter','carrot','apple','peach','rice','cherry','fruit','chocolate','lemon','banana','cheesecake','pecan','raspberry','strawberry','chocolate','toffee','orange','blueberry'}
            for sortKeys in SecondaryItemKey:
                if sortKeys in fooditem:
                    return "DessertTable",x,sortKeys
                    
    SecondaryItemKey = {'pasta','omelette','stew','chili','dhal','lasagna','macaroni','masala','tofu stew','casserole','teryaki','spaghetti','eggs'}
    for sortKeys in SecondaryItemKey:
        if sortKeys in fooditem:
            return "VegetarianTable",'vegetarian',sortKeys
    return "notfound"

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
        
        itemInfo = findKeysandTable(itemToQuery)
        if itemInfo[0] == 'n':
            speak_output = "Sorry, I couldn't find the item you were looking for."
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    # .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .response
            ) 
        #session token service api request
        sts_client = boto3.client('sts')
        assumed_role_object=sts_client.assume_role(RoleArn="<ARN_role>", RoleSessionName="AssumeRoleSession1")
        credentials=assumed_role_object['Credentials']

        # 2. Make a new DynamoDB instance with the assumed role credentials
        dynamodb = boto3.resource('dynamodb',
                      aws_access_key_id=credentials['AccessKeyId'],
                      aws_secret_access_key=credentials['SecretAccessKey'],
                      aws_session_token=credentials['SessionToken'],
                      region_name='us-east-1')

        # 3. Perform DynamoDB operations on the table
        try:
            table = dynamodb.Table(itemInfo[0])
            response = table.query(KeyConditionExpression = Key('MainItem').eq(itemInfo[1]) & Key('SecondaryKey').eq(itemInfo[2]))
            speak_output = 'I have found {quantity} {item} in the inventory'.format(quantity=response['Items'][0]['Quantity'], item=response['Items'][0]['ItemName'])
            #speak_output = "debug yo"
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
        
        itemInfo = findKeysandTable(itemToRemove)
        if itemInfo[0] == 'n':
            speak_output = "Sorry, I couldn't find the item you were looking for."
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    # .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .response
            ) 
        
        #session token service api request
        sts_client = boto3.client('sts')
        assumed_role_object=sts_client.assume_role(RoleArn="<ARN_role>", RoleSessionName="AssumeRoleSession1")
        credentials=assumed_role_object['Credentials']

        # 2. Make a new DynamoDB instance with the assumed role credentials
        dynamodb = boto3.resource('dynamodb',
                      aws_access_key_id=credentials['AccessKeyId'],
                      aws_secret_access_key=credentials['SecretAccessKey'],
                      aws_session_token=credentials['SessionToken'],
                      region_name='us-east-1')

        # 3. Perform DynamoDB operations on the table
        try:
            table = dynamodb.Table(itemInfo[0])
            queryResponse = table.query(KeyConditionExpression = Key('MainItem').eq(itemInfo[1]) & Key('SecondaryKey').eq(itemInfo[2]))
            inventoryQuantity = int(queryResponse['Items'][0]['Quantity'])
            speak_output = 'yo debug'
            if inventoryQuantity < int(quantityOfItem):
                speak_output = 'Sorry, I cannot remove the requested amount. There are only {inventoryQuantity} in the inventory.'.format(inventoryQuantity=inventoryQuantity)
            else:
                quantityLeft = int(inventoryQuantity) - int(quantityOfItem)
                response = table.update_item(
                    Key={
                        'MainItem': itemInfo[1],
                        'SecondaryKey': itemInfo[2]
                    },
                    UpdateExpression="set Quantity=:q",
                    ExpressionAttributeValues={
                        ':q': quantityLeft,
                    },
                    ReturnValues="UPDATED_NEW"
                )
                speak_output = 'I have removed {quantityOfItem}. There are {quantityLeft} {itemToRemove} left'.format(quantityOfItem=quantityOfItem, quantityLeft=quantityLeft,itemToRemove=queryResponse['Items'][0]['ItemName'])
            
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
        
        itemInfo = findKeysandTable(itemToAdd)
        if itemInfo[0] == 'n':
            speak_output = "Sorry, I couldn't find the item you were looking for."
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    # .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .response
            ) 
        #session token service api request
        sts_client = boto3.client('sts')
        assumed_role_object=sts_client.assume_role(RoleArn="<ARN_role>", RoleSessionName="AssumeRoleSession1")
        credentials=assumed_role_object['Credentials']

        # 2. Make a new DynamoDB instance with the assumed role credentials
        dynamodb = boto3.resource('dynamodb',
                      aws_access_key_id=credentials['AccessKeyId'],
                      aws_secret_access_key=credentials['SecretAccessKey'],
                      aws_session_token=credentials['SessionToken'],
                      region_name='us-east-1')

        # 3. Perform DynamoDB operations on the table
        try:
            table = dynamodb.Table(itemInfo[0])
            queryResponse = table.query(KeyConditionExpression = Key('MainItem').eq(itemInfo[1]) & Key('SecondaryKey').eq(itemInfo[2]))
            totalQuantity = int(queryResponse['Items'][0]['Quantity']) + int(quantityOfItem)
            response = table.update_item(
                Key={
                    'MainItem': itemInfo[1],
                    'SecondaryKey': itemInfo[2]
                },
                UpdateExpression="set Quantity=:q",
                ExpressionAttributeValues={
                    ':q': quantityOfItem,
                },
                ReturnValues="UPDATED_NEW"
            )
            speak_output = 'I have added {quantityOfItem} {itemToAdd} to the inventory'.format(quantityOfItem=totalQuantity,itemToAdd=itemToAdd)
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
