import datetime as dt
import pytz
import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit_qs as stqs
from calendar_class import CALENDAR_IMPRINT, EVENT_IMPRINT, TASK_IMPRINT

# OAuth 2.0 setup
CLIENT_SECRETS_FILE = "oauth-web-app.json"
SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/tasks"]

# REDIRECT_URI = 'https://calendar-tasks.streamlit.app'  # Обновите этот URL на ваш реальный адрес
REDIRECT_URI = 'http://localhost:8501'

def create_flow():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    return flow

def get_service(credentials):
    service_calendar = build('calendar', 'v3', credentials=credentials)
    service_tasks = build('tasks', 'v1', credentials=credentials)
    return service_calendar, service_tasks

def get_calendar_tasks(service_calendar, service_tasks, n_events=3):
    try:
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

def add_event(service_calendar, date=None):
    if date is None:
        now = dt.datetime.now()
        tomorrow = now + dt.timedelta(days=1)
        date = dt.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 15, 0, 0)
        
    google_timezone = service_calendar.settings().get(setting='timezone').execute()
    start_time = date.isoformat()
    end_time = (date + dt.timedelta(hours=1)).isoformat()
    
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
    try:
        event = service_calendar.events().insert(calendarId='primary', body=event).execute()
        st.success(f'Event created: {event.get("htmlLink")}')
    except HttpError as error:
        st.error(f"An error occurred: {error}")

def main():
    st.title("Google Calendar and Tasks")

    flow = create_flow()
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    if 'credentials' not in st.session_state:
        code = stqs.from_query_args("code")
        if code:
            flow.fetch_token(code=code)
            credentials = flow.credentials
            st.session_state.credentials = credentials
            st.rerun()
        else:
            if st.button('Authorize with Google'):
                st.write('Click the link below to authorize:')
                st.markdown(f'<a href="{authorization_url}" target="_blank">Authorize</a>', unsafe_allow_html=True)
    else:
        credentials = st.session_state.credentials
        st.write('Authorization successful!')

        service_calendar, service_tasks = get_service(credentials)

        menu = ["View Events and Tasks", "Add Event"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "View Events and Tasks":
            st.subheader("View Events and Tasks")
            n_events = st.number_input("Number of events to retrieve", min_value=1, max_value=10, value=3)
            events, task_lists = get_calendar_tasks(service_calendar, service_tasks, n_events)

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
                add_event(service_calendar, event_date)

if __name__ == "__main__":
    main()
