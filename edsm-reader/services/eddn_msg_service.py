from datetime import datetime
from typing import Optional, List

import structlog

from models.eddn_msg import EDDNMsg
from ..decorator.logit import logit
from ..io.database import Database

EDDN_MESSAGE_SELECT_BY_ID = '''
select id, "schema", header, message, recv_date, sync_date
from eddn_message
where id = %(id)s
'''

EDDN_MESSAGE_SELECT_UNREAD = '''
select id, "schema", header, message, recv_date, sync_date
from eddn_message
where sync_date is null
'''

EDDN_MESSAGE_INSERT = '''
insert into eddn_message 
("schema", header, message, recv_date, sync_date)
values (%(schema)s, 
        %(header)s, 
        %(message)s, 
        %(recv_date)s, 
        %(sync_date)s);
'''

EDDN_MESSAGE_UPDATE_BY_ID = '''
update eddn_message
set "schema" = %(schema)s,
    header = %(header)s,
    message = %(message)s,
    recv_date = %(recv_date)s,
    sync_date = %(sync_date)s
where id = %(id)s
'''

EDDN_MESSAGE_DELETE_BY_ID = '''
delete from eddn_message
where id = %(id)s
'''


class EDDNMessageService:
    _io_db: Database

    def __init__(self, db: Database):
        self._io_db = db
        self._log = structlog.get_logger()

    @logit
    def read_eddn_message_by_id(self, uuid: str) -> Optional[EDDNMsg]:
        raw_data = self._io_db.exec_db_read(EDDN_MESSAGE_SELECT_BY_ID, {'id': uuid})
        if raw_data is not None and len(raw_data) > 0:
            return EDDNMsg(raw_data[0])
        else:
            self._log.debug(f'No {EDDNMsg.__name__} found')
            return None

    @logit
    def read_eddn_message_unread(self) -> Optional[List[EDDNMsg]]:
        raw_data = self._io_db.exec_db_read(EDDN_MESSAGE_SELECT_BY_ID)
        if raw_data is not None and len(raw_data) > 0:
            eddn_msgs = []
            for data in raw_data:
                eddn_msgs.append(EDDNMsg(data))
            return eddn_msgs
        else:
            self._log.debug(f'No {EDDNMsg.__name__} found')
            return None

    @logit
    def create_eddn_message(self, eddn_msg: EDDNMsg) -> None:
        eddn_msg.recv_date = datetime.now()
        self._io_db.exec_db_write(EDDN_MESSAGE_INSERT, eddn_msg.to_dict_for_db())

    @logit
    def update_eddn_message(self, eddn_msg: EDDNMsg) -> None:
        self._io_db.exec_db_write(EDDN_MESSAGE_UPDATE_BY_ID, eddn_msg.to_dict_for_db())

    @logit
    def delete_sync_state_by_id(self, uuid: str) -> None:
        self._io_db.exec_db_write(EDDN_MESSAGE_DELETE_BY_ID, {'id': uuid})
