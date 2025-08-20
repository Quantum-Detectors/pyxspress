"""
Xspress Odin acquisition script

A basic Python script which configures and runs a basic acquisition using the
ADOdin interface.
"""

import logging
import os
import time
from threading import Event

import click
import h5py
from epics import caget, camonitor, camonitor_clear, caput
from matplotlib import pyplot

# Logging
logging_format = "[%(asctime)s][%(levelname)7s][%(name)s] %(message)s"
formatter = logging.Formatter(logging_format)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger = logging.getLogger("pyadodin")
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

base_pv_name = "XSPRESS:CAM"
base_file_pv_name = "XSPRESS:OD"


@click.command(
    help="Run a basic internally-triggered acquisition and optionally save the data.",
    context_settings={"show_default": True, "help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)
@click.option("-i", "--images", type=int, default=10, help="Number of images")
@click.option(
    "-t",
    "--acquire_time",
    type=float,
    default=0.1,
    help="Acquisition time per frame in seconds",
)
@click.option(
    "-fd", "--file_dir", type=str, default="/data/odin-testing", help="File directory"
)
@click.option("-fn", "--file_name", type=str, default=None, help="File name")
@click.option(
    "-pl", "--plot", is_flag=True, default=False, help="Enable plotting of some data"
)
@click.option(
    "-pa",
    "--plot_all",
    is_flag=True,
    default=False,
    help="Plot every image (caps out at 10 plots to avoid sluggishness)",
)
@click.option(
    "-tm",
    "--trigger_mode",
    type=int,
    default=2,
    help="Trigger mode (2: Burst, 3:Hardware)",
)
def main(
    images: int,
    acquire_time: float,
    file_name: str | None,
    file_dir: str,
    plot: bool,
    plot_all: bool,
    trigger_mode: int,
):
    """Main entry point for acquisition script

    Args:
        images (int): Number of images
        acquire_time (float): Acquisition time per frame (seconds)
        file_name (Optional[str]): File name prefix
        file_dir (str): File directory
        plot (bool): Plot some data
        plot_all (bool): Plot all data (up to 5 frames for performance)
    """
    if plot_all and not plot:
        plot = True

    logger.info(f"Capturing {images} images with exposure time {acquire_time:<.4f}s")

    # Check we are connected and configuration is valid
    connect_and_configure_check()

    # Set up acquisition
    reset_state()

    caput(f"{base_pv_name}:AcquireTime", acquire_time)
    caput(f"{base_pv_name}:NumImages", images)
    caput(f"{base_pv_name}:TriggerMode", trigger_mode)

    if file_name is not None:
        setup_file_writing(file_dir, file_name, images, acquire_time)

    # Monitor detector state transitions
    acquire_event = Event()
    idle_event = Event()

    def detector_state_monitor(pvname: str, value: int, char_value: str, **kw):
        """Called when the DetectorState_RBV PV updates

        Args:
            pvname (str): Name of the PV
            value (int): Value of the PV in native type
            char_value (str): String representation of value (e.g. if enum)
        """
        nonlocal acquire_event
        if value == 1:
            acquire_event.set()
            idle_event.clear()
        elif value == 0:
            acquire_event.clear()
            idle_event.set()

    camonitor(f"{base_pv_name}:DetectorState_RBV", callback=detector_state_monitor)

    # Monitor buffers free
    buffer_monitors = setup_buffer_monitors(2)

    # Start acquisition and wait for acquisition to begin
    acquire()
    if not acquire_event.wait(3.0):
        logger.warning("Timeout waiting for acquisition start")

    wait_acquisition_complete(images, acquire_time)

    # Wait for idle detector state
    logger.info("Waiting for detector to become idle")
    if not idle_event.wait(3.0):
        raise ValueError("Timeout waiting for idle state")
    else:
        logger.info("Xspress is now idle")
    if file_name is not None:
        write_success = wait_file_writing_complete(images)

    if plot:
        # Plot in non-blocking mode
        pyplot.ion()

        # Stop monitors
        camonitor_clear(f"{base_pv_name}:DetectorState_RBV")
        for monitor in buffer_monitors:
            monitor.clear_monitor()

        # Plot
        if file_name is not None and write_success is True:
            num_channels = caget(f"{base_pv_name}:MAX_NUM_CHANNELS_RBV")
            plot_data(file_dir, file_name, images, plot_all, num_channels)

        create_buffer_monitor_plot(buffer_monitors)

        pyplot.show()
        input("Press any key to exit (and close all plots)\n> ")


def connect_and_configure_check():
    # Check we are connected
    if caget(f"{base_pv_name}:CONNECTED") == 0:
        raise ValueError("Odin not connected to Xspress")
    elif caget(f"{base_pv_name}:RECONNECT_REQUIRED") == 1:
        logger.info("Reconfigure required - reconfiguring")
        caput(f"{base_pv_name}:RECONFIGURE", 1, wait=True)

        logger.info("Waiting for Odin to reconnect")
        connect_timeout = 5
        waited_time = 0.0
        while caget(f"{base_pv_name}:CONNECTED") == 0:
            time.sleep(0.1)
            waited_time += 0.1

            if waited_time > connect_timeout:
                raise ValueError("Odin did not reconnect to Xspress in time")

        logger.info("Reconfigure complete")


def reset_state():
    """Reset the state of Odin to make sure the system is idle"""
    if caget(f"{base_pv_name}:Acquire") == 1:
        caput(f"{base_pv_name}:Acquire", 0, wait=True)

    if caget(f"{base_file_pv_name}:Capture") == 1:
        caput(f"{base_file_pv_name}:Capture", 0, wait=True)


def setup_file_writing(
    file_dir: str, file_name: str, num_images: int, acquire_time: float
):
    """Set up the file writing

    Args:
        file_dir (str): File directory to write data to
        file_name (str): Base file name
        num_images (int): Number of images
        acquire_time (float): Acquisition time. Used to determine chunking


    Raises:
        ValueError: Exception if target filenames already exist
    """
    # Check paths don't already exist
    if check_no_overwrite(file_dir, file_name) is False:
        raise ValueError(
            f"Files for base name {file_dir}/{file_name} "
            "already exist. Choose a different filename or path"
        )

    logger.info(f"Saving data to {file_dir}/{file_name}_(A_000000/B_000000/meta).h5")

    caput(f"{base_file_pv_name}:FilePath", file_dir)
    caput(f"{base_file_pv_name}:FileName", file_name)

    caput(f"{base_file_pv_name}:NumCapture", num_images)

    # Each channel will be saved into its own dataset
    caput(f"{base_file_pv_name}:ImageHeight", 1)
    caput(f"{base_file_pv_name}:ImageWidth", 4096)

    # TODO: work out why chunking makes data sad part way through
    # frame_chunking = max(int(1 / acquire_time), 1)
    frame_chunking = 1
    logger.info(f"Frames per chunk: {frame_chunking}")

    caput(f"{base_file_pv_name}:NumFramesChunks", frame_chunking)
    caput(f"{base_file_pv_name}:NumFramesChunks", 1)
    caput(f"{base_file_pv_name}:NumRowChunks", 1)
    caput(f"{base_file_pv_name}:NumColChunks", 4096)

    # Start the file writer and wait for it to be ready
    caput(f"{base_file_pv_name}:Capture", 1, wait=True, timeout=5)


def acquire():
    """Request the acquisition to begin"""
    logger.info("Starting acquisition")
    caput(f"{base_pv_name}:Acquire", 1)
    time.sleep(2.0)  # Wait due to counter not resetting :(


def wait_acquisition_complete(images: int, acquire_time: float):
    """Wait for the acquisition to finish

    Args:
        images (int): Number of expected images
        acquire_time (float): Acquire time (used for monitoring)

    Raises:
        ValueError: Raised if wrong number of images acquired
        ValueError: Raised if timeout occurred
    """
    logger.info(
        f"Waiting for acquisition to complete (estimated {images * acquire_time:<.2f}s)"
    )
    timeout = images * acquire_time + 10.0
    time_waited = 0.0
    poll_interval = 0.2
    next_update_percent = 10  # Log update every 10%

    acquired_images = caget(f"{base_pv_name}:ArrayCounter_RBV")
    while acquired_images < images:
        time.sleep(poll_interval)
        time_waited += poll_interval
        acquired_images = caget(f"{base_pv_name}:ArrayCounter_RBV")

        if acquired_images / images > next_update_percent / 100.0:
            logger.info(f" - {next_update_percent}% complete")
            next_update_percent += 10

        if acquired_images > images:
            raise ValueError(f"Expected {images} frames. Got {acquired_images}")

        elif time_waited > timeout:
            raise ValueError(
                f"Timed out waiting for {images} frames after {timeout}s. "
                f"Got {acquired_images} frames."
            )

    logger.info(f"Acquisition complete after {time_waited:<.2f}s")


def wait_file_writing_complete(images: int) -> bool:
    """Wait for the file writer to finish

    Args:
        images (int): Number of expected images

    Returns:
        bool: True for success or False for failure
    """
    logger.info("Waiting for file saving to complete")
    logger.info(" - Waiting for data frames")

    poll_interval = 1.0

    # Initial poll
    prev_written_images = caget(f"{base_file_pv_name}:NumCaptured_RBV")
    time.sleep(poll_interval)
    written_images = caget(f"{base_file_pv_name}:NumCaptured_RBV")

    # Now start monitoring until progress stalls
    while written_images != prev_written_images:
        prev_written_images = written_images
        time.sleep(poll_interval)
        written_images = caget(f"{base_file_pv_name}:NumCaptured_RBV")

    logger.info(" - Waiting for metadata frames")

    # Wait for the MetaWriter
    prev_meta_frames = caget(f"{base_file_pv_name}:META:FramesWritten_RBV")
    time.sleep(poll_interval)
    meta_frames = caget(f"{base_file_pv_name}:META:FramesWritten_RBV")
    while meta_frames != prev_meta_frames:
        prev_meta_frames = meta_frames
        time.sleep(poll_interval)
        meta_frames = caget(f"{base_file_pv_name}:META:FramesWritten_RBV")

    logger.info(" - Waiting for files to close")

    # Manually close the file(s) and wait for feedback
    max_timeout = 10.0
    wait_time = 0.0
    caput(f"{base_file_pv_name}:Capture", 0)
    while caget(f"{base_file_pv_name}:Capture_RBV") != 0:
        time.sleep(0.5)
        wait_time += 0.5
        if wait_time > max_timeout:
            logger.warning("Timed out waiting for files to close")
            break

    logger.info(" - Files closed")

    # Check the number of images written - 2 file writers create twice the number of
    # "half" images
    if written_images != 2 * images:
        logger.error(f"Wrote {written_images} half-images when {2 * images} expected")
        return False
    else:
        logger.info("File saving complete")
        return True


def check_no_overwrite(file_dir: str, file_name: str) -> bool:
    """Check if the provided file directory and base name prefix will overwrite
    any existing files.

    Args:
        file_dir (str): File directory
        file_name (str): Base file name

    Returns:
        bool: True if no overwriting will occur
    """
    no_overwrite = True

    a_file = f"{file_dir}/{file_name}_A_000000.h5"
    b_file = f"{file_dir}/{file_name}_B_000000.h5"
    meta_file = f"{file_dir}/{file_name}_meta.h5"

    if os.path.exists(a_file):
        logger.warning(f"File for file writer A already exists: {a_file}")
        no_overwrite = False

    if os.path.exists(b_file):
        logger.warning(f"File for file writer B already exists: {b_file}")
        no_overwrite = False

    if os.path.exists(meta_file):
        logger.warning(f"File for metadata already exists: {meta_file}")
        no_overwrite = False

    return no_overwrite


def plot_data(
    file_dir: str, file_name: str, images: int, plot_all: bool, num_channels: int
):
    """Plot the captured data

    Args:
        file_dir (str): File directory
        file_name (str): Base file name
        num_channels (int): Number of channels in system
    """
    logger.info("Plotting data")

    a_file = f"{file_dir}/{file_name}_A_000000.h5"
    b_file = f"{file_dir}/{file_name}_B_000000.h5"

    if plot_all:
        max_index = min(images, 5)
        logger.info(f"Plotting {max_index} images")
    else:
        max_index = 1

    for image in range(max_index):
        # Create the figure
        _, axs = pyplot.subplots(2, num_channels // 2)

        with h5py.File(a_file) as input_file:
            for i in range(num_channels // 2):
                dataset = f"mca_{i}"
                logger.info(f"Channel {i} data shape: {input_file[dataset].shape}")
                data = input_file[dataset][image, 0, :]
                axs[0, i].plot(data)
                axs[0, i].set_title(f"Channel {i}")

        with h5py.File(b_file) as input_file:
            for i in range(num_channels // 2, num_channels):
                dataset = f"mca_{i}"
                logger.info(f"Channel {i} data shape: {input_file[dataset].shape}")
                data = input_file[dataset][image, 0, :]
                col = i - num_channels // 2
                axs[1, col].plot(data)
                axs[1, col].set_title(f"Channel {i}")


class OdinBufferMonitor:
    def __init__(self, process_number: int):
        """Create an Odin buffer monitor

        Args:
            process_number (int): Odin processor/receiver pair number
        """
        self.process_number = process_number
        self.pv_name = f"XSPRESS:OD{process_number}:FreeBuffers_RBV"
        # Populate the first value with the current value
        self.buffers_history: list[int] = [caget(self.pv_name)]
        self.start_monitor()

    def add_buffer_value(self, pvname: str, value: int, **kw):
        """Callback from PV monitor to add the value to the list

        Args:
            pvname (str): Name of PV
            value (int): New value
        """
        self.buffers_history.append(value)

    def start_monitor(self):
        """Start the PV monitoring which stores the updates too"""
        camonitor(self.pv_name, callback=self.add_buffer_value)

    def clear_monitor(self):
        """Stop the PV monitor

        An additional value is added at the end to create a sensible looking
        plot if the PV never updated since the monitor was started.
        """
        camonitor_clear(self.pv_name)

        if len(self.buffers_history) == 1:
            self.buffers_history.append(caget(self.pv_name))


def setup_buffer_monitors(num_processes: int) -> list[OdinBufferMonitor]:
    """Set up monitors to watch the number of buffers free in the Odin
    processor/receiver pairs

    Args:
        num_processes (int): Number of Odin process pairs

    Returns:
        List[ProcessBufferMonitor]: List of monitor objects
    """
    monitors: list[OdinBufferMonitor] = []
    for process_number in range(1, num_processes + 1):
        monitors.append(OdinBufferMonitor(process_number))

    return monitors


def create_buffer_monitor_plot(buffer_monitors: list[OdinBufferMonitor]):
    """Create a single plot containing the buffer monitor data

    Args:
        buffer_monitors (List[OdinBufferMonitor]): Buffer monitors
    """
    _, axs = pyplot.subplots(1, len(buffer_monitors))

    index = 0
    for monitor in buffer_monitors:
        axs[index].plot(monitor.buffers_history)
        axs[index].set_title(f"Process {index}")
        axs[index].set_xlabel("History")
        axs[index].set_ylabel("Free buffers")
        index += 1


if __name__ == "__main__":
    main()
