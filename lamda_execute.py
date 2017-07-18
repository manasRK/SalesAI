"""
This demonstrates an implementation of the Lex Code Hook Interface in order to serve a sample bot 
which acts as a virtual assistant for a salesperson.

Bot, Intent, and Slot models which are compatible with this have been created after relevant testing.
The data and context information are saved to DynamoDB for referring to at a later point in time and set calendar reminders.
"""

import os
import time
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response

def SaveBookHotel(intent_request):
    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('HotelBookings')

    # Get Variables from the Bot Response
    Location = get_slots(intent_request)["Location"]
    CheckInDate = get_slots(intent_request)["CheckInDate"]
    Nights = get_slots(intent_request)["Nights"]
    RoomType = get_slots(intent_request)["RoomType"]

    logger.info("Data Received: Location: %s, CheckInDate: %s, Nights:%s, RoomType:%s", 
                    Location, CheckInDate, Nights, RoomType)
    
    # Construct the Dictionary
    DynamoDict = {
        'Location':Location, 
        'CheckInDate':CheckInDate, 
        'Nights':Nights, 
        'RoomType':RoomType,
        'BookingID': Location+RoomType+str(CheckInDate)
    }
    
    table.put_item(Item=DynamoDict)
    logger.info("Data Pushed Sucessfully to database")
    
    return close(intent_request['sessionAttributes'],
             'Fulfilled',
             {'contentType': 'PlainText',
              'content': 'Thank you. Your room booking for {} nights in {} has been scheduled.'.format(Nights, Location)})
 
def SaveBookCar(intent_request):
    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('CarBookings')

    # Get Variables from the Bot Response
    PickUpCity = get_slots(intent_request)["PickUpCity"]
    PickUpDate = get_slots(intent_request)["PickUpDate"]
    ReturnDate = get_slots(intent_request)["ReturnDate"]
    DriverAge = get_slots(intent_request)["DriverAge"]
    CarType = get_slots(intent_request)["CarType"]

    logger.info("Data Received: PickUpCity: %s, PickUpDate: %s, ReturnDate:%s, DriverAge:%s, CarType:%s", 
                    PickUpCity, PickUpDate, ReturnDate, DriverAge, CarType)
    # Construct the Dictionary
    DynamoDict = {
        'PickUpCity':PickUpCity, 
        'PickUpDate':PickUpDate, 
        'ReturnDate':ReturnDate, 
        'DriverAge':DriverAge,
        'CarType': CarType,
        'BookingID': PickUpCity+CarType+str(ReturnDate)
    }
    
    table.put_item(Item=DynamoDict)
    logger.info("Data Pushed Sucessfully to database")
    return close(intent_request['sessionAttributes'],
             'Fulfilled',
             {'contentType': 'PlainText',
              'content': 'Thank you. Your car booking for {} on {} has been scheduled.'.format(PickUpCity, PickUpDate)})
   
def SaveSalesCalendar(intent_request):
    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('SalesCalendar')

    # Get Variables from the Bot Response
    Location = get_slots(intent_request)["LocationSales"]
    Client = get_slots(intent_request)["Client"]
    Time = get_slots(intent_request)["Time"]
    Product = get_slots(intent_request)["Product"]
    DayOfMeeting = get_slots(intent_request)["DayOfMeeting"]
    
    logger.info("Data Received: Location: %s, Client: %s, Time:%s, Product:%s, DayOfMeeting: %s", Location, Client, Time, Product, DayOfMeeting)
    
    # Construct the Dictionary
    DynamoDict = {
        'Client':Client, 
        'Location':Location, 
        'Product':Product, 
        'Time':Time,
        'DayOfMeeting':DayOfMeeting,
        'ClientDate': Client+str(DayOfMeeting)+Product
    }
    
    table.put_item(Item=DynamoDict)
    logger.info("Data Pushed Sucessfully to database")
    return close(intent_request['sessionAttributes'],
             'Fulfilled',
             {'contentType': 'PlainText',
              'content': 'Thank you. Your meeting with {} has been scheduled. We will send you a reminder 2 hours before your meeting.'.format(Client)})

    
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'SalesInquiry':
        return SaveSalesCalendar(intent_request)
    
    if intent_name == 'BookHotel':
        return SaveBookHotel(intent_request)
    
    if intent_name == 'BookCar':
        return SaveBookCar(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
