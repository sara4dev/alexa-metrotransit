"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import requests
import json

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetDepartureTime":
        return get_departure_time_in_session(intent, session)
    else:
        raise ValueError("Invalid intent")
        

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa MN Transit Skills. " \
                    "Please tell me which direction, route & stop to find the next departure time."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your direction, route & stop to find the next departure time by saying, " \
                    "ask Metro Transit departure time from Hennepin for route 7 north bound."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa MN Transit Skills. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def get_departure_time_in_session(intent, session):
    """ Get the next departure time for given direction, route & stop and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Direction' in intent['slots'] and 'Route' in intent['slots'] and 'Stop' in intent['slots']:
        direction = intent['slots']['Direction']['value']
        route = intent['slots']['Route']['value']
        stop = intent['slots']['Stop']['value']

        session_attributes = {"direction": direction, "route": route, "stop": stop}
        print(session_attributes)

        url = "http://svc.metrotransit.org/NexTrip/" + route + "/" + get_direction_id(direction) + "/" + get_stop_id(route, direction, stop)
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers)
        print(response.text)
        data = json.loads(response.text)

        speech_output = direction +  ", route " + route + ", from stop " + stop + ", departs at " + data[0]["DepartureText"]
        reprompt_text = ""
    else:
        speech_output = "I'm not sure if got the direction, route & stop. " \
                        "Please try again."
        reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_direction_id(direction):
    if direction.lower() == "north bound":
        print("north bound direction id 4")
        return "4"
    elif direction.lower() == "south bound":
        print("south bound direction id 1")
        return "1"
    elif direction.lower() == "east bound":
        print("east bound direction id 2")
        return "2"
    elif direction.lower() == "west bound":
        print("west bound direction id 3")
        return "3"

def get_stop_id(route, direction, stop):
    url = "http://svc.metrotransit.org/NexTrip/Stops/" + route + "/" + get_direction_id(direction)
    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    print(response.text)
    data = json.loads(response.text)
    print(stop.lower())
    for stop_record in data:
        print(stop_record["Text"].lower())
        if stop.lower() in stop_record["Text"].lower():
            print("Stop id for " + stop_record["Text"] + "is " + stop_record["Value"])
            return stop_record["Value"]
        else:
            print("Stop not found")

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
