# notifications.py
# This file sends push notifications using OneSignal
# To use this, you need to sign up at onesignal.com and get your API key

#Enter your keys here
MY_APP_ID  = "YOUR_APP_ID_HERE"
MY_API_KEY = "YOUR_API_KEY_HERE"

# We need these built-in Python tools to send data over the internet
import urllib.request
import json
import threading #Stops the UI from freezing


# This function sends a notification to everyone using the app
def send_notification(title, message):
    """POST a broadcast notification to all OneSignal subscribers."""

    # This is the website address we send the notification to
    url = "https://onesignal.com/api/v1/notifications"

    # This is the info we are sending (like filling out a form)
    notification_data = {
        "app_id": MY_APP_ID,
        "included_segments": ["All"],   # send to ALL users
        "headings": {"en": title},      # the bold title of the notification
        "contents": {"en": message}     # the message under the title
    }

    # Convert our data to a format the internet understands
    data_to_send = json.dumps(notification_data).encode("utf-8")

    # Set up the request (like writing a letter before mailing it)
    request = urllib.request.Request(
        url,
        data = data_to_send,
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + MY_API_KEY
        },
        method = "POST"
    )

    # Try to send the notification
    # If something goes wrong, print the error instead of crashing
    try:
        response = urllib.request.urlopen(request)
        print("Notification sent successfully!")

    except Exception as error:
        print("Something went wrong sending the notification:")
        print(error)


# This function is called when someone submits a lost or found report
def notify_new_report(report_type, item_name, location):

    # Build the title and message using the report info
    title   = "New " + report_type + " Item: " + item_name
    message = "Location: " + location

    threading.Thread(
        target=send_notification,
        args=(title, message),
        daemon=True  # thread closes automatically when the app exits
    ).start()
