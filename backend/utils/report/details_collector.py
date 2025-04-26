from dataclasses import dataclass
from typing import Tuple

@dataclass
class ReportDetails:
    proctor: str
    block: str
    date: str
    subject: str
    room: str
    start_time: str
    end_time: str
    num_students: str

class DetailsCollector:
    @staticmethod
    def collect_details(widgets) -> ReportDetails:
        return ReportDetails(
            proctor=widgets['proctor'].text(),
            block=widgets['block'].get_block_text(),
            date=widgets['date'].date().toString("yyyy-MM-dd"),
            subject=widgets['subject'].text(),
            room=widgets['room'].get_room_text(),
            start_time=widgets['start_time'].get_time_24h(),
            end_time=widgets['end_time'].get_time_24h(),
            num_students=widgets['num_students'].text()
        )

    @staticmethod
    def unpack_details(details: ReportDetails) -> Tuple:
        return (
            details.proctor,
            details.block,
            details.date,
            details.subject,
            details.room,
            details.start_time,
            details.end_time,
            details.num_students
        )
