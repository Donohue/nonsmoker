/**
 
 Copyright 2016 Brian Donohue.
 
*/

'use strict';

// Route the incoming request based on type (LaunchRequest, IntentRequest,
// etc.) The JSON body of the request is provided in the event parameter.
exports.handler = function (event, context) {
    try {
        console.log("event.session.application.applicationId=" + event.session.application.applicationId);

        /**
         * Uncomment this if statement and populate with your skill's application ID to
         * prevent someone else from configuring a skill that sends requests to this function.
         */
		 
//     if (event.session.application.applicationId !== "amzn1.echo-sdk-ams.app.05aecccb3-1461-48fb-a008-822ddrt6b516") {
//         context.fail("Invalid Application ID");
//      }

        if (event.session.new) {
            onSessionStarted({requestId: event.request.requestId}, event.session);
        }

        if (event.request.type === "LaunchRequest") {
            onLaunch(event.request,
                event.session,
                function callback(sessionAttributes, speechletResponse) {
                    context.succeed(buildResponse(sessionAttributes, speechletResponse));
                });
        } else if (event.request.type === "IntentRequest") {
            onIntent(event.request,
                event.session,
                function callback(sessionAttributes, speechletResponse) {
                    context.succeed(buildResponse(sessionAttributes, speechletResponse));
                });
        } else if (event.request.type === "SessionEndedRequest") {
            onSessionEnded(event.request, event.session);
            context.succeed();
        }
    } catch (e) {
        context.fail("Exception: " + e);
    }
};

/**
 * Called when the session starts.
 */
function onSessionStarted(sessionStartedRequest, session) {
    console.log("onSessionStarted requestId=" + sessionStartedRequest.requestId
        + ", sessionId=" + session.sessionId);

    // add any session init logic here
}

/**
 * Called when the user invokes the skill without specifying what they want.
 */
function onLaunch(launchRequest, session, callback) {
    console.log("onLaunch requestId=" + launchRequest.requestId
        + ", sessionId=" + session.sessionId);

    var cardTitle = "Nonsmoker"
    var speechOutput = "You can ask how many days since Brian quit, or how much money brian has saved since he quit."
    callback(session.attributes,
        buildSpeechletResponse(cardTitle, speechOutput, "", true));
}

/**
 * Called when the user specifies an intent for this skill.
 */
function onIntent(intentRequest, session, callback) {
    console.log("onIntent requestId=" + intentRequest.requestId
        + ", sessionId=" + session.sessionId);

    var intent = intentRequest.intent,
        intentName = intentRequest.intent.name;

    // dispatch custom intents to handlers here
    if (intentName == 'TimeFirstPersonIntent') {
        handleTimeRequest(intent, session, callback, true);
    }
    else if (intentName == 'TimeThirdPersonIntent') {
        handleTimeRequest(intent, session, callback, false);
    }
    else if (intentName == 'MoneyFirstPersonIntent') {
        handleMoneyRequest(intent, session, callback, true);
    }
    else if (intentName == 'MoneyThirdPersonIntent') {
        handleMoneyRequest(intent, session, callback, false);
    }
    else {
        throw "Invalid intent";
    }
}

/**
 * Called when the user ends the session.
 * Is not called when the skill returns shouldEndSession=true.
 */
function onSessionEnded(sessionEndedRequest, session) {
    console.log("onSessionEnded requestId=" + sessionEndedRequest.requestId
        + ", sessionId=" + session.sessionId);

    // Add any cleanup logic here
}

function numberOfDaysSinceQuitting() {
    var quitTime = 1431885600;
    var currentTime = Math.round(new Date().getTime()/1000.0);
    var timeElapsedInSecs = currentTime - quitTime;
    var daysInSecs = 86400;
    return Math.round(timeElapsedInSecs / daysInSecs);
}

function handleTimeRequest(intent, session, callback, isFirstPerson) {
    var subject = isFirstPerson? "you": "brian";
    var phrase = isFirstPerson? "Nice job!": "You should pat him on the back.";
    var speechOutput = "It's been " + numberOfDaysSinceQuitting() + " days since " + subject + " quit smoking. " + phrase;
    callback(session.attributes,
        buildSpeechletResponseWithoutCard(speechOutput, "", "true"));
}

function handleMoneyRequest(intent, session, callback, isFirstPerson) {
    var firstSubject = isFirstPerson? "You've": "Brian has";
    var secondSubject = isFirstPerson? "you": "brian";
    var phrase = isFirstPerson? "Wow. Such savings.": "What do you think he's spent all that extra money on?";
    var speechOutput = firstSubject + " saved about " + numberOfDaysSinceQuitting() * 15 + " dollars since " + secondSubject + " quit smoking. " + phrase;
    callback(session.attributes,
        buildSpeechletResponseWithoutCard(speechOutput, "", "true"));
}

// ------- Helper functions to build responses -------

function buildSpeechletResponse(title, output, repromptText, shouldEndSession) {
    return {
        outputSpeech: {
            type: "PlainText",
            text: output
        },
        card: {
            type: "Simple",
            title: title,
            content: output
        },
        reprompt: {
            outputSpeech: {
                type: "PlainText",
                text: repromptText
            }
        },
        shouldEndSession: shouldEndSession
    };
}

function buildSpeechletResponseWithoutCard(output, repromptText, shouldEndSession) {
    return {
        outputSpeech: {
            type: "PlainText",
            text: output
        },
        reprompt: {
            outputSpeech: {
                type: "PlainText",
                text: repromptText
            }
        },
        shouldEndSession: shouldEndSession
    };
}

function buildResponse(sessionAttributes, speechletResponse) {
    return {
        version: "1.0",
        sessionAttributes: sessionAttributes,
        response: speechletResponse
    };
}

