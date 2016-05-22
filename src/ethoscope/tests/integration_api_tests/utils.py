import tempfile
import os
from ethoscope.core.monitor import Monitor
from ethoscope.hardware.input.cameras import MovieVirtualCamera
from ethoscope.utils.io import SQLiteResultWriter
from ethoscope.trackers.adaptive_bg_tracker import AdaptiveBGModel
from ethoscope.drawers.drawers import DefaultDrawer
from ethoscope.roi_builders.target_roi_builder import SleepMonitorWithTargetROIBuilder
from ethoscope.hardware.interfaces.interfaces import HardwareConnection
from _constants import VIDEO, DRAW_FRAMES


def test_stimulator(StimulatorClass, InterfaceClass):
    tmp = tempfile.mkstemp(suffix="_ethoscope_test.db")[1]

    print("Making a tmp db: " + tmp)
    cam = MovieVirtualCamera(VIDEO, drop_each=15)
    rb = SleepMonitorWithTargetROIBuilder()
    rois = rb.build(cam)
    cam.restart()

    connection = HardwareConnection(InterfaceClass)
    try:
        # stimulators = [MockSDStimulator(connection,min_inactive_time= 10) for _ in rois ]
        stimulators = [StimulatorClass(connection) for _ in rois]
        mon = Monitor(cam, AdaptiveBGModel, rois, stimulators=stimulators)
        drawer = DefaultDrawer(draw_frames=DRAW_FRAMES)

        with SQLiteResultWriter(tmp , rois) as rw:
            mon.run(result_writer=rw, drawer=drawer)

    finally:
        print("Removing temp db (" + tmp+ ")")
        os.remove(tmp)
        connection.stop()