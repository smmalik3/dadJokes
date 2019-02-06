#!/usr/bin/env python
"""
Copyright (c) 2019. All rights reserved.
@author:        salman malik
@created:       1/25/19
@last modified: 2/6/19
"""
from __future__ import print_function
from botocore.vendored import requests
from datetime import datetime
import json

# --------------- Release Notes ---------------
# v1.0 - Initial Version - January 25, 2019
# ---------------------------------------------

# --------------- Credits ---------------
# Thank you to https://icanhazdadjoke.com/api for the wonderful api
# ---------------------------------------

# --------------- Skill Invocation ---------------
# You can ask Alexa to ruin someone's day by asking for a random dad joke. You get a new joke every time you ask her. You can initiate the skill by saying:
#
# "Alexa, open dad jokes."
#
# After the welcome message you can then say any of the following:
#
# "Tell me a joke"
# "Tell me a fresh joke"
# "Tell me a dad joke"
# "Let's get this over with."
#
# Alternatively, to skip the welcome message and dive straight into some painful comedy (can we even call it that?) you can say the following:
#
# "Alexa, ask dad jokes to tell me a joke."
# "Alexa, ask dad jokes for a joke."
# "Alexa, ask dad jokes to tell me a fresh joke."
# "Alexa, ask dad jokes for a fresh joke."
# "Alexa, ask dad jokes to tell me a dad joke."
# "Alexa, ask dad jokes for a dad joke."
# "Alexa, ask dad jokes to end my suffering."
# ---------------------------------------------

# --------------- Helpers that build all of the responses ---------------

#NOTE: can't use the word 'speechlet' in text output for cards
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_ssml_speechlet_response(title, speech_output, text_output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': speech_output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': text_output
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

# --------------- Functions that control the skill's behavior ---------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "<speak> <s>Welcome to Dad Jokes.</s> <s> For a fresh dad joke, <break strength='medium'/> say, <break strength='medium'/> tell me a joke.</s> </speak>"
    text_output = "Welcome to Dad Jokes. For a fresh dad joke, say, 'Tell me a joke.'"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Welcome to Dad Jokes. For a fresh dad joke, say, 'Tell me a joke.'"
    should_end_session = False

    return build_response(session_attributes, build_ssml_speechlet_response(
        card_title, speech_output, text_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "No more jokes for you!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True

    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# Method for getting dad joke
def get_dad_joke(intent, session):
    url = 'https://icanhazdadjoke.com/'
    headers = {'Accept': 'application/json'}
    r = requests.get(url, headers=headers)
    r = r.json()
    joke = r['joke']

    card_title = joke
    speech_output = joke
    should_end_session = True
    
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Events ---------------

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

    session = session 
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "DadJokeIntent":
        return get_dad_joke(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Main handler ---------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])


    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])