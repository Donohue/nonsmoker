from __future__ import print_function
import boto3
import datetime
import dateutil.parser
import random

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    #if (event['session']['application']['applicationId'] !=
    #    "amzn1.echo-sdk-ams.app.[YOUR-APP-ID]"):
    #    raise ValueError("Invalid Application ID")

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

def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    user_id = session['user']['userId']
    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('nonsmoker')
    return get_time_intent(table, user_id)

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('nonsmoker')

    user_id = session['user']['userId']
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == 'GetTimeIntent':
        return get_time_intent(table, user_id)
    elif intent_name == 'SetTimeIntent':
        return set_time_intent()
    elif intent_name == 'SetDayMonthIntent':
        return set_day_month_intent(table, user_id, intent)
    elif intent_name == 'SetYearIntent':
        return set_year_intent(table, user_id, session, intent)
    elif intent_name == "AMAZON.HelpIntent":
        return help_response()
    else:
        raise ValueError("Invalid intent: %s" % intent_name)


# --------------- Functions that control the skill's behavior ------------------
def get_time_intent(table, user_id):
    response = table.get_item(
        Key={"user_id": user_id}
    )
    
    try:
        quit_date = response['Item']['quit_date']
    except KeyError:
        return set_time_intent()

    return build_response(
        {},
        build_speechlet_response(time_response(quit_date))
    )

def set_time_intent():
    return build_response(
        {},
        build_speechlet_response(
            "What month and day did you stop smoking?",
            should_end_session=False
        )
    )

def set_day_month_intent(table, user_id, intent):
    day_month = intent['slots']['day_month']['value']
    date = dateutil.parser.parse(day_month)
    return build_response(
        {'month': date.month, 'day': date.day},
        build_speechlet_response(
            "Great, you stopped smoking on %s %s. Which year did you stop smoking?" % (date.strftime('%B'), day_date_string(date.day)),
            should_end_session=False
        )
    )

def set_year_intent(table, user_id, session, intent):
    try:
        month = session['attributes']['month']
        day = session['attributes']['day']
    except KeyError:
        return set_time_intent()

    year = intent['slots']['year']['value']
    quit_date = '%s/%s/%s' % (month, day, year)
    if datetime_from_date(quit_date) > today():
        return build_response(
            {},
            build_speechlet_response(
                "The stop date you gave, %s %s %s, is in the future. What month and day did you stop smoking?" % (month_from_date(quit_date), day_date_string(day), year),
                should_end_session=False
            )
        )

    table.put_item(Item={
        'user_id': user_id,
        'quit_date': quit_date
    })

    return build_response(
        {},
        build_speechlet_response(
            "Your stop date has been set to %s %s, %s. %s" % (month_from_date(quit_date), day_date_string(day), year, time_response(quit_date))
        )
    )

def help_response():
    return build_response(
        {},
        build_speechlet_response(
            "You can ask how long it has been since you stopped smoking or set your stop date."
        )
    )

def random_encouragement():
    encouragement = [
        'Good work!',
        'Nice job!',
        'Keep it up!',
        'Congrats!'
    ]
    return random.choice(encouragement)

def time_response(quit_date):
    if datetime_from_date(quit_date) == today():
        return "Lao Tzu once said, the journey of a thousand miles begins with a single step. Congratulations on becoming a nonsmoker."
    else:
        return "It has been %s since you stopped smoking. %s" % (time_elapsed(quit_date), random_encouragement())

def unit_string(string, quantity):
    return string if quantity == 1 else string + 's'

def month_string(quantity):
    return unit_string('month', quantity)

def year_string(quantity):
    return unit_string('year', quantity)

def day_string(quantity):
    return unit_string('day', quantity)

def month_from_date(date):
    return datetime_from_date(date).strftime('%B')

def datetime_from_date(date):
    return datetime.datetime.strptime(date, '%m/%d/%Y')

def today():
    return datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

def time_elapsed(quit_date):
    date = datetime_from_date(quit_date)
    delta = today() - date
    years = delta.days / 365
    months = (delta.days % 365) / 30
    days = delta.days % 365 % 30
    
    if years >= 1 and delta.days % 365 == 0:
        return '%d %s' % (years, year_string(years))
    elif years >= 1 and months >= 1 and days == 0:
        return '%d %s and %d %s' % (years, year_string(years), months, month_string(months))
    elif years >= 1 and months >= 1:
        return '%d %s, %d %s, and %d %s' % (years, year_string(years), months, month_string(months), days, day_string(days))
    elif years >= 1:
        return '%d %s and %d %s' % (years, year_string(years), days, day_string(days))
    elif months >= 1 and days == 0:
        return '%d %s' % (month, month_string(months))
    elif months >= 1:
        return '%d %s and %d %s' % (months, month_string(months), days, day_string(days))
    else:
        return '%d %s' % (days, day_string(days))

def day_date_string(day):
    return '%d%s' % (day, day_suffix(day))

def day_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        return "th"
    else:
        return ["st", "nd", "rd"][day % 10 - 1]

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(output, card_title=None, card_content=None,
                             reprompt='', should_end_session=True):
    response =  {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt
            }
        },
        'shouldEndSession': should_end_session
    }

    if card_title and card_content:
        response['card'] = {
            'type': 'Simple',
            'title': card_title,
            'content': card_content
        }

    return response

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

