class KeyboardError(Exception): pass

class AlreadyRecordingError(KeyboardError): pass
class NotRecordingError(KeyboardError): pass
class NotReplayingError(KeyboardError): pass
class AlreadyReplayingError(KeyboardError): pass