import os.path
import datetime as dt
import pytz
import random

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from calendar_class import CALENDAR_IMPRINT, EVENT_IMPRINT, TASK_IMPRINT


SCOPES = ["https://www.googleapis.com/auth/calendar",
          "https://www.googleapis.com/auth/tasks"]


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
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def get_calendar_tasks(n_events = 10):

    creds = get_or_create_token()

    try:
        service_calendar = build("calendar", "v3", credentials=creds)
        service_tasks = build("tasks", "v1", credentials=creds)

        # Call the Calendar API
        # original: 2024-07-05T07:50:05.154483Z
        # new:      2024-07-05T07:50:39.722132+00:00Z
        # Получение текущего времени по местному времени (UTC+7)
        # local_timezone_offset = timedelta(hours=7)
        # now_local = datetime.now(timezone.utc) + local_timezone_offset
        # now_local_iso = now_local.isoformat()
        # 'Z' indicates UTC time
        google_timezone = service_calendar.settings().get(setting='timezone').execute()
        local_tz = pytz.timezone(google_timezone['value'])
        now = dt.datetime.now(local_tz).isoformat()
        print(f'timezone: {local_tz}, time iso: {now}')
        
        print(f"Getting the upcoming {n_events} events")
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

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

        # Call the Tasks API
        results = service_tasks.tasklists().list(maxResults=10).execute()
        items = results.get("items", [])

        if not items:
            print("No task lists found.")
            return
        tasks = []
        print("Task lists:")
        for item in items:
            print(f"Task list name: {item['title']} \n (id: {item['id']})")

            result_one_list = service_tasks.tasks().list(
                tasklist=item['id']).execute()
            tasks_one_list = result_one_list.get('items', [])
            for i, task in enumerate(tasks_one_list, 1):
                tasks.append(task)
                print(f"    {i}: {task['title']} ({task['id']})")
                if task.get('notes'):
                    print(f'      notes: {task['notes']}')
                if task.get('due'):
                    print(f'      due: {task['due']}')
        
        return events, tasks
    except HttpError as error:
        print(f"An error occurred: {error}")


def add_event(summary: str='No summary argument passed',
              description: str='no description argument passed',
              location: str='home/online',
              date=None, 
              duration=60):
    # 1. ACTUALIZE CALENDAR AND TASKS
    if date is None:
        # Устанавливаем день и время по умолчанию: завтра в 15:00
        now = dt.datetime.now()
        tomorrow = now + dt.timedelta(days=1)
        date = dt.datetime(tomorrow.year, tomorrow.month,
                           tomorrow.day, 15, 0, 0)
    # Форматируем дату для Google Calendar API
    
    start_time = date.isoformat()
    # Длительность события 1 час
    end_time = (date + dt.timedelta(minutes=duration)).isoformat()

    creds = get_or_create_token()
    service = build("calendar", "v3", credentials=creds)
    google_timezone = service.settings().get(setting='timezone').execute()
    event = {
        'summary': summary,
        'description': description,
        'location': location,
        'colorId': random.randint(1, 11),
        'start': {
            'dateTime': start_time,
            # 'timeZone': 'Asia/Ho_Chi_Minh',
            'timeZone': google_timezone['value'],
            
        },
        'end': {
            'dateTime': end_time,
            'timeZone': google_timezone['value'],
        },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f'Event created: {event.get("htmlLink")}')


if __name__ == "__main__":
    offline_calendar = CALENDAR_IMPRINT()
    while True:
        print(
            '''
1           || get calendar events and tasks
2           || add_event
3           || print offline calendar
4           || print offline tasks
5           || print full offline calendar objects
6           || print full offline calendar summary 
any         || exit   
            '''
        )
        user_action = input('choice: ')
        try:
            user_action = int(user_action)
        except ValueError:
            break

        match user_action:
            case 1:
                events, tasks = get_calendar_tasks()
                offline_calendar.load_events(events)
                offline_calendar.load_tasks(tasks)
            case 2:
                add_event()
            case 3:  
                for e in offline_calendar.events:
                    print(e)
                print('example of event object:', repr(events[0])) if len(offline_calendar.events)>0  else None
            case 4:
                for t in offline_calendar.tasks:
                    print(t)
                print('example of task object:', repr(tasks[0])) if len(offline_calendar.tasks)>0  else None
            case 5:
                print(offline_calendar)
            case 6:
                offline_calendar.summary()                
            case _:
                break
