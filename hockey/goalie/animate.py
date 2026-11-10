import numpy as np
import json
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

# Default connections between joints. Change these as you please
connections = [
    ("RIGHT_EYE", "LEFT_EYE"),
    ("RIGHT_EYE", "NOSE"),
    ("LEFT_EYE", "NOSE"),
    ("RIGHT_EYE", "RIGHT_EAR"),
    ("LEFT_EYE", "LEFT_EAR"),
    ("NOSE", "NECK"),
    ("NECK", "RIGHT_SHOULDER"),
    ("NECK", "LEFT_SHOULDER"),
    ("RIGHT_SHOULDER", "RIGHT_ELBOW"),
    ("LEFT_SHOULDER", "LEFT_ELBOW"),
    ("RIGHT_ELBOW", "RIGHT_WRIST"),
    ("LEFT_ELBOW", "LEFT_WRIST"),
    ("RIGHT_SHOULDER", "RIGHT_HIP"),
    ("LEFT_SHOULDER", "LEFT_HIP"),
    ("RIGHT_HIP", "LEFT_HIP"),
    ("RIGHT_HIP", "RIGHT_KNEE"),
    ("LEFT_HIP", "LEFT_KNEE"),
    ("RIGHT_KNEE", "RIGHT_ANKLE"),
    ("LEFT_KNEE", "LEFT_ANKLE"),
]


def _to_array(values):
    """Convert a list of [x, y, z] (or null) to an (N, 3) array, with NaN where data is missing."""
    return np.array([v if v is not None else [np.nan] * 3 for v in values], dtype=float)


def animate_shot(
    path_to_json,
    connections=connections,
    track_goalie=True,
    buffer=8.0,
    zlim=6.0,
    elev=30.0,
    azim=180.0,
    goalie_color="#841FD1",
    goalie_lw=3,
    puck_color="black",
    puck_size=4,
    puck_trail_frames=5,
    show_rink=True,
    notebook_mode=True,
):
    """
    Function to animate a single shot of 3D goalie pose and puck tracking data.

    Parameters:
    -----------
    - path_to_json: str
        The path to the JSON file containing the shot data.
    - connections: list of tuples
        A list of tuples, where each tuple contains two strings representing the joints to connect.
    - track_goalie: bool
        How the view is framed:
        True  = follow the goalie's MID_HIP, showing +/- buffer feet around them each frame.
                Best for looking at goalie movement; the puck is only visible once it is near the goalie.
        False = fixed view covering the goalie and the full puck path (plus buffer feet of padding).
                Best for seeing the whole shot; the goalie appears smaller.
        Combine with elev/azim to choose the viewing angle, e.g.
        elev=30, azim=180 (default): from the slot, looking toward the net;
        elev=50, azim=180: high view from the slot, similar to an overhead camera behind the shooter;
        elev=15, azim=270: side view from the boards;
        elev=90, azim=180: top-down view.
    - buffer: float
        For track_goalie=True: half-width (feet) of the view window around the goalie
        (smaller = tighter on the goalie, e.g. 5; larger = more of the puck approach, e.g. 12).
        For track_goalie=False: padding (feet) around the goalie and puck path.
    - zlim: float
        The limit for the z-axis height (feet).
    - elev: float
        The elevation angle (degrees) for the 3D view. 0 = ice level, 90 = straight down.
    - azim: float
        The azimuth angle (degrees) for the 3D view. 180 looks toward the net from the slot; 270 is a side view.
    - goalie_color: str
        The color to use for the goalie lines.
    - goalie_lw: float
        The line width to use for the goalie lines.
    - puck_color: str
        The color to use for the puck.
    - puck_size: float
        The marker size to use for the puck.
    - puck_trail_frames: int
        Number of previous puck positions drawn as fading circles behind the puck.
        Wider spacing between circles = faster puck. Set to 0 to disable.
    - show_rink: bool
        Whether to show the rink in the background (requires mplhockey).
    - notebook_mode: bool
        Whether function is used within a Jupyter notebook.

    Returns:
    --------
    - anim: matplotlib.animation.FuncAnimation
        The animation object created by the function.
    """

    if notebook_mode:
        plt.rcParams["animation.html"] = "jshtml"

    if show_rink:
        try:
            from mplhockey import NHLRink
        except ModuleNotFoundError:
            print("mplhockey not installed. Cannot show rink.")
            show_rink = False

    with open(path_to_json, "r") as f:
        data = json.load(f)

    # The block of code below returns a dictionary, where each key is a 3D time series for coordinates of a joint.
    # Missing values (null in the JSON) become NaN, which matplotlib simply does not draw.
    goalie_joint_dict = {}
    puck_data = []
    for frame_data in data["tracking"]:
        for joint, xyz in frame_data["data"]["goalie"].items():
            goalie_joint_dict.setdefault(joint, []).append(xyz)
        puck_data.append(frame_data["data"]["puck"])

    goalie_joint_dict = {joint: _to_array(values) for joint, values in goalie_joint_dict.items()}
    puck_data = _to_array(puck_data)

    metadata = data["metadata"]
    n_frames = len(data["tracking"])
    sampling_rate = metadata["goalie_sampling_rate__hz"]
    times_s = np.array([frame_data["time"] for frame_data in data["tracking"]]) / 1000

    # Animate the data
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d", computed_zorder=False)
    ax.set_proj_type("persp")
    ax.set_axis_off()
    ax.view_init(elev=elev, azim=azim)

    if show_rink:
        NHLRink(units="ft").draw3d(ax)

    # Prepare the lines to be updated
    lines = {connection: ax.plot([], [], [], c=goalie_color, lw=goalie_lw, zorder=10)[0] for connection in connections}
    # One marker per trail position, fading out with age (index 0 = most recent)
    puck_trail = [
        ax.plot(
            [],
            [],
            [],
            "o",
            markersize=puck_size,
            c=puck_color,
            alpha=0.6 * (1 - k / (puck_trail_frames + 1)),
            zorder=20,
        )[0]
        for k in range(1, puck_trail_frames + 1)
    ]
    (puck,) = ax.plot([], [], [], "o", markersize=puck_size, c=puck_color, zorder=21)
    time_text = ax.text2D(0.02, 0.95, "", transform=ax.transAxes, fontsize=12, fontweight="bold")

    def update(frame):

        if track_goalie:  # track the goalie, with a view centered on their MID_HIP joint
            mh = goalie_joint_dict["MID_HIP"][frame]
            if np.all(np.isfinite(mh)):
                ax.set_xlim([mh[0] - buffer, mh[0] + buffer])
                ax.set_ylim([mh[1] - buffer, mh[1] + buffer])
                ax.set_zlim(0, zlim)
                # Equal scaling in feet so the goalie is not stretched
                ax.set_box_aspect((2 * buffer, 2 * buffer, zlim))

        else:  # track the puck and goalie together, with a fixed view
            all_xy = np.vstack([goalie_joint_dict["MID_HIP"][:, :2], puck_data[:, :2]])
            all_xy = all_xy[np.isfinite(all_xy).all(axis=1)]
            xlim = (all_xy[:, 0].min() - buffer, min(all_xy[:, 0].max() + buffer, 100.0))
            ylim = (all_xy[:, 1].min() - buffer, all_xy[:, 1].max() + buffer)
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
            ax.set_zlim(0, zlim)
            # Equal scaling in feet so the goalie is not stretched
            ax.set_box_aspect((xlim[1] - xlim[0], ylim[1] - ylim[0], zlim))

        # Update the line data for each connection
        for part1, part2 in connections:
            segment = np.stack([goalie_joint_dict[part1][frame], goalie_joint_dict[part2][frame]])
            lines[(part1, part2)].set_data_3d(segment[:, 0], segment[:, 1], segment[:, 2])

        # Update puck data
        current = puck_data[frame : frame + 1]
        puck.set_data_3d(current[:, 0], current[:, 1], current[:, 2])
        for k, marker in enumerate(puck_trail, start=1):
            past = puck_data[frame - k : frame - k + 1] if frame - k >= 0 else np.full((1, 3), np.nan)
            marker.set_data_3d(past[:, 0], past[:, 1], past[:, 2])

        time_text.set_text(f"{metadata['shot_number']} | t = {times_s[frame]:.2f} s")

    plt.close()

    anim = FuncAnimation(fig, update, frames=n_frames, interval=1000 / sampling_rate)
    return anim
