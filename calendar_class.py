import json


class EVENT_IMPRINT:
    def __init__(self, event_data: dict):
        # Инициализируем все атрибуты значениями по умолчанию
        self.kind = "calendar#event"
        self.etag = ""
        self.id = ""
        self.status = ""
        self.htmlLink = ""
        self.created = None
        self.updated = None
        self.summary = ""
        self.description = ""
        self.location = ""
        self.colorId = ""
        self.creator = {
            "id": "",
            "email": "",
            "displayName": "",
            "self": False
        }
        self.organizer = {
            "id": "",
            "email": "",
            "displayName": "",
            "self": False
        }
        self.start = {
            "date": None,
            "dateTime": None,
            "timeZone": ""
        }
        self.end = {
            "date": None,
            "dateTime": None,
            "timeZone": ""
        }
        self.endTimeUnspecified = False
        self.recurrence = []
        self.recurringEventId = ""
        self.originalStartTime = {
            "date": None,
            "dateTime": None,
            "timeZone": ""
        }
        self.transparency = ""
        self.visibility = ""
        self.iCalUID = ""
        self.sequence = 0
        self.attendees = []
        # 'attendees': [
        #     {'email': 'lpage@example.com'},
        #     {'email': 'sbrin@example.com'},
        # ],
        self.attendeesOmitted = False
        self.extendedProperties = {
            "private": {},
            "shared": {}
        }
        self.hangoutLink = ""
        self.conferenceData = {
            "createRequest": {
                "requestId": "",
                "conferenceSolutionKey": {
                    "type": ""
                },
                "status": {
                    "statusCode": ""
                }
            },
            "entryPoints": [],
            "conferenceSolution": {
                "key": {
                    "type": ""
                },
                "name": "",
                "iconUri": ""
            },
            "conferenceId": "",
            "signature": "",
            "notes": ""
        }
        self.gadget = {
            "type": "",
            "title": "",
            "link": "",
            "iconLink": "",
            "width": 0,
            "height": 0,
            "display": "",
            "preferences": {}
        }
        self.anyoneCanAddSelf = False
        self.guestsCanInviteOthers = False
        self.guestsCanModify = False
        self.guestsCanSeeOtherGuests = False
        self.privateCopy = False
        self.locked = False
        self.reminders = {
            "useDefault": False,
            "overrides": []
        }
        # 'reminders': {
        #     'useDefault': False,
        #     'overrides': [
        #         {'method': 'email', 'minutes': 24 * 60},
        #         {'method': 'popup', 'minutes': 10},
        #     ],
        # },
        self.source = {
            "url": "",
            "title": ""
        }
        self.workingLocationProperties = {
            "type": "",
            "homeOffice": None,
            "customLocation": {
                "label": ""
            },
            "officeLocation": {
                "buildingId": "",
                "floorId": "",
                "floorSectionId": "",
                "deskId": "",
                "label": ""
            }
        }
        self.outOfOfficeProperties = {
            "autoDeclineMode": "",
            "declineMessage": ""
        }
        self.focusTimeProperties = {
            "autoDeclineMode": "",
            "declineMessage": "",
            "chatStatus": ""
        }
        self.attachments = []
        self.eventType = ""

        # Обновляем атрибуты значениями из переданного словаря
        for key, value in event_data.items():
            setattr(self, key, value)
    
    
    def set_reminder(self, method: str, time):
        if method not in ['email', 'popup']:
            raise ValueError("Invalid reminder method. Must be 'email' or 'popup'.")
        if time is None:
            raise AttributeError("Time must be specified.")
    
    def __repr__(self):
        return json.dumps(self.__dict__, default=str, indent=4)

class TASK_IMPRINT:
    def __init__(self, task_data: dict):
        # Инициализируем все атрибуты значениями по умолчанию
        self.kind = ""
        self.id = ""
        self.etag = ""
        self.title = ""
        self.updated = ""
        self.selfLink = ""
        self.parent = ""
        self.position = ""
        self.notes = ""
        self.status = ""
        self.due = ""
        self.completed = ""
        self.deleted = False
        self.hidden = False
        self.links = []
        self.webViewLink = ""
        self.assignmentInfo = None

        # Обновляем атрибуты значениями из переданного словаря
        for key, value in task_data.items():
            setattr(self, key, value)

    def __repr__(self):
        return json.dumps(self.__dict__, default=str, indent=4)

    # def __str__(self):
    #     return f"Task ID: {self.id}, Title: {self.title}, Status: {self.status}"
    
    
class CALENDAR_IMPRINT:
    def __init__(self, current_time=None, calendar_start_time=None, calendar_end_time=None):
        self._events = []
        self._tasks = []
        self.current_time = current_time
        self.calendar_start_time = calendar_start_time
        self.calendar_end_time = calendar_end_time

    @property
    def events(self):
        return self._events

    def add_event(self, event: EVENT_IMPRINT):
        self._events.append(event)

    def load_events(self, events_data: list):
        for event_data in events_data:
            event = EVENT_IMPRINT(event_data)
            self.add_event(event)
    @property
    def tasks(self):
        return self._tasks
    
    def add_task(self, task: TASK_IMPRINT):
        self._tasks.append(task)
        
    def load_tasks(self, tasks_data: list):
        for task_data in tasks_data:
            task = TASK_IMPRINT(task_data)
            self.add_task(task)
    
    def __repr__(self):
        events_repr = [repr(event) for event in self._events]
        tasks_repr = [repr(task) for task in self._tasks]
        return f"CALENDAR_IMPRINT(events={events_repr}) \n TASKS_IMPRINT(tasks={tasks_repr})"

    # def __str__(self):
    #     return f"Calendar ID: {self._calendar_id}, Number of Events: {len(self._events)}"

    
