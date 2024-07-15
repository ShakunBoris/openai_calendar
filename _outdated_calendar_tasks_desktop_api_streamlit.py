import os.path
import datetime as dt
import pytz
import streamlit as st

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/tasks"]

def get_or_create_token():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file("token.json")
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            # creds = flow.run_console()
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_calendar_tasks(n_events=3):
    creds = get_or_create_token()

    try:
        service_calendar = build("calendar", "v3", credentials=creds)
        service_tasks = build("tasks", "v1", credentials=creds)

        google_timezone = service_calendar.settings().get(setting='timezone').execute()
        local_tz = pytz.timezone(google_timezone['value'])
        now = dt.datetime.now(local_tz).isoformat()
        
        events_result = (
            service_calendar.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=n_events,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        task_lists = []
        results = service_tasks.tasklists().list(maxResults=10).execute()
        items = results.get("items", [])

        for item in items:
            result_one_list = service_tasks.tasks().list(
                tasklist=item['id']).execute()
            tasks_one_list = result_one_list.get('items', [])
            task_lists.append({"title": item["title"], "tasks": tasks_one_list})

        return events, task_lists

    except HttpError as error:
        st.error(f"An error occurred: {error}")
        return [], []

def add_event(date=None):
    if date is None:
        now = dt.datetime.now()
        tomorrow = now + dt.timedelta(days=1)
        date = dt.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 15, 0, 0)
    start_time = date.isoformat()
    end_time = (date + dt.timedelta(hours=1)).isoformat()

    creds = get_or_create_token()
    service = build("calendar", "v3", credentials=creds)
    google_timezone = service.settings().get(setting='timezone').execute()
    event = {
        'summary': 'Google I/O 2015',
        'description': 'A chance to hear more about Google\'s developer products.',
        'location': 'somewhere',
        'colorId': 1,
        'start': {
            'dateTime': start_time,
            'timeZone': google_timezone['value'],
        },
        'end': {
            'dateTime': end_time,
            'timeZone': google_timezone['value'],
        },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    st.success(f'Event created: {event.get("htmlLink")}')


def main():
    st.title("Google Calendar and Tasks")

    menu = ["View Events and Tasks", "Add Event"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "View Events and Tasks":
        st.subheader("View Events and Tasks")
        n_events = st.number_input("Number of events to retrieve", min_value=1, max_value=10, value=3)
        events, task_lists = get_calendar_tasks(n_events)

        st.header("Upcoming Events")
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            st.write(f"{start} - {event['summary']}")

        st.header("Task Lists")
        for task_list in task_lists:
            st.subheader(task_list["title"])
            for task in task_list["tasks"]:
                st.write(f"{task['title']}")
                if task.get('notes'):
                    st.write(f"Notes: {task['notes']}")
                if task.get('due'):
                    st.write(f"Due: {task['due']}")

    elif choice == "Add Event":
        st.subheader("Add Event")
        date = st.date_input("Select date", dt.datetime.now().date() + dt.timedelta(days=1))
        time = st.time_input("Select time", dt.time(15, 0))
        event_date = dt.datetime.combine(date, time)
        if st.button("Add Event"):
            add_event(event_date)

if __name__ == "__main__":
    main()
