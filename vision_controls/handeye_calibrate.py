"""
Eye-to-hand calibration for a fixed RealSense D435 and a myCobot 320 Pi.

Configuration assumed here: the camera is bolted to the overhead boom and does
not move; a ChArUco board is mounted rigidly to the arm's tool flange. The
unknown being solved for is the transform from the camera frame to the robot
base frame.

Run modes:
    python handeye_calibrate.py board     # generate a printable board
    python handeye_calibrate.py collect   # capture pose pairs interactively
    python handeye_calibrate.py solve     # solve and report the residual

Dependencies: opencv-contrib-python, pyrealsense2, numpy, ikpy, pymycobot.
"""

import sys
import json
import numpy as np
import cv2

# OpenCV 5.x dropped calibrateHandEye and interpolateCornersCharuco from the
# Python bindings. Stay on the 4.x line for this script.
if not hasattr(cv2, "calibrateHandEye"):
    raise SystemExit(
        f"OpenCV {cv2.__version__} does not expose calibrateHandEye.\n"
        "Install a 4.x build:  pip install opencv-contrib-python==4.10.0.84"
    )


# =====================================================================
# Board definition -- EDIT THESE to match your printed board
# =====================================================================
SQUARES_X = 5              # number of chessboard squares across
SQUARES_Y = 7              # number of chessboard squares down
SQUARE_LENGTH_M = 0.030    # MEASURE THIS with a caliper after printing
MARKER_LENGTH_M = 0.022    # MEASURE THIS too; must be < SQUARE_LENGTH_M

ARUCO_DICT = cv2.aruco.DICT_5X5_100
POSE_FILE = "handeye_poses.json"
RESULT_FILE = "cam2base.json"


# ---------------------------------------------------------------------
# OpenCV 4.7 changed the aruco API. These wrappers work either way.
# ---------------------------------------------------------------------
def _get_dictionary():
    if hasattr(cv2.aruco, "getPredefinedDictionary"):
        return cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    return cv2.aruco.Dictionary_get(ARUCO_DICT)


def _get_board(dictionary):
    if hasattr(cv2.aruco, "CharucoBoard") and not hasattr(cv2.aruco, "CharucoBoard_create"):
        return cv2.aruco.CharucoBoard(
            (SQUARES_X, SQUARES_Y), SQUARE_LENGTH_M, MARKER_LENGTH_M, dictionary
        )
    return cv2.aruco.CharucoBoard_create(
        SQUARES_X, SQUARES_Y, SQUARE_LENGTH_M, MARKER_LENGTH_M, dictionary
    )


def _detect_charuco(gray, board, dictionary):
    """Returns (charuco_corners, charuco_ids) or (None, None)."""
    if hasattr(cv2.aruco, "ArucoDetector"):
        det = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
        corners, ids, _ = det.detectMarkers(gray)
    else:
        corners, ids, _ = cv2.aruco.detectMarkers(gray, dictionary)

    if ids is None or len(ids) < 4:
        return None, None

    retval, ch_corners, ch_ids = cv2.aruco.interpolateCornersCharuco(
        corners, ids, gray, board
    )
    if retval is None or retval < 6:
        return None, None
    return ch_corners, ch_ids


def _board_object_points(board, ch_ids):
    """3D coordinates of the detected chessboard corners, board frame."""
    if hasattr(board, "getChessboardCorners"):
        all_pts = board.getChessboardCorners()
    else:
        all_pts = board.chessboardCorners
    return np.array([all_pts[i[0]] for i in ch_ids], dtype=np.float32)


# =====================================================================
# Mode: board -- write a printable PNG
# =====================================================================
def make_board(path="charuco_board.png", dpi=300):
    dictionary = _get_dictionary()
    board = _get_board(dictionary)

    # size the image so the print comes out at true scale
    w_px = int(SQUARES_X * SQUARE_LENGTH_M * 1000 / 25.4 * dpi)
    h_px = int(SQUARES_Y * SQUARE_LENGTH_M * 1000 / 25.4 * dpi)

    if hasattr(board, "generateImage"):
        img = board.generateImage((w_px, h_px))
    else:
        img = board.draw((w_px, h_px))

    cv2.imwrite(path, img)
    print(f"wrote {path}  ({w_px}x{h_px} px, print at {dpi} dpi, NO scaling)")
    print("After printing, measure one square and one marker with a caliper")
    print("and update SQUARE_LENGTH_M / MARKER_LENGTH_M in this file.")


# =====================================================================
# Mode: collect -- capture (robot pose, board pose) pairs
# =====================================================================
def collect(n_target=18):
    import pyrealsense2 as rs
    from pymycobot import MyCobot320Socket

    dictionary = _get_dictionary()
    board = _get_board(dictionary)

    mc = MyCobot320Socket("129.8.233.110", 9000)   # adjust port for your setup

    pipeline = rs.pipeline()
    cfg = rs.config()
    cfg.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    profile = pipeline.start(cfg)

    intr = profile.get_stream(rs.stream.color).as_video_stream_profile().intrinsics
    K = np.array([[intr.fx, 0, intr.ppx],
                  [0, intr.fy, intr.ppy],
                  [0, 0, 1]], dtype=np.float64)
    dist = np.array(intr.coeffs, dtype=np.float64)
    print("color intrinsics:", K.ravel())

    samples = []
    print("\nMove the arm by hand or by script to a new pose, then press SPACE")
    print("to capture. Press Q when done. Aim for varied ORIENTATION, not just")
    print("varied position -- rotation is unobservable without it.\n")

    try:
        while True:
            frames = pipeline.wait_for_frames()
            color = np.asanyarray(frames.get_color_frame().get_data())
            gray = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)

            ch_corners, ch_ids = _detect_charuco(gray, board, dictionary)
            vis = color.copy()
            ok = ch_corners is not None
            if ok:
                cv2.aruco.drawDetectedCornersCharuco(vis, ch_corners, ch_ids)

            cv2.putText(vis, f"captured {len(samples)}/{n_target}  "
                             f"{'BOARD OK' if ok else 'no board'}",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0) if ok else (0, 0, 255), 2)
            cv2.imshow("charuco", vis)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            if key == ord(' ') and ok:
                obj = _board_object_points(board, ch_ids)
                img_pts = ch_corners.reshape(-1, 2).astype(np.float32)
                success, rvec, tvec = cv2.solvePnP(
                    obj, img_pts, K, dist, flags=cv2.SOLVEPNP_ITERATIVE
                )
                if not success:
                    print("  solvePnP failed, skipping")
                    continue

                angles = mc.get_angles()
                if angles is None:
                    print("  get_angles() returned None, skipping")
                    continue

                samples.append({
                    "joint_angles_deg": list(angles),
                    "rvec_target2cam": rvec.ravel().tolist(),
                    "tvec_target2cam": tvec.ravel().tolist(),
                    "n_corners": int(len(ch_ids)),
                })
                print(f"  captured {len(samples)}: {len(ch_ids)} corners, "
                      f"t = {np.round(tvec.ravel(), 4)}")
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()

    with open(POSE_FILE, "w") as f:
        json.dump({"K": K.tolist(), "dist": dist.tolist(), "samples": samples}, f, indent=2)
    print(f"\nwrote {len(samples)} samples to {POSE_FILE}")


# =====================================================================
# Mode: solve -- run calibrateHandEye and report the residual
# =====================================================================
def load_chain(urdf_path="mycobot_320.urdf"):
    from ikpy.chain import Chain
    return Chain.from_urdf_file(urdf_path)


def fk_pose(chain, angles_deg):
    """Forward kinematics -> 4x4 flange pose in the base frame."""
    q = np.zeros(len(chain.links))
    active = [i for i, a in enumerate(chain.active_links_mask) if a]
    for k, i in enumerate(active):
        q[i] = np.deg2rad(angles_deg[k])
    return chain.forward_kinematics(q)


def solve(urdf_path="mycobot_320.urdf"):
    with open(POSE_FILE) as f:
        data = json.load(f)
    samples = data["samples"]
    if len(samples) < 6:
        raise SystemExit(f"only {len(samples)} samples; need at least 6, ideally 15+")

    chain = load_chain(urdf_path)

    R_b2g, t_b2g, R_t2c, t_t2c = [], [], [], []
    T_g2b_all = []

    for s in samples:
        T_g2b = fk_pose(chain, s["joint_angles_deg"])
        T_g2b_all.append(T_g2b)

        # eye-to-hand: feed the INVERSE of the flange pose
        R_gb = T_g2b[:3, :3]
        t_gb = T_g2b[:3, 3]
        R_b2g.append(R_gb.T)
        t_b2g.append(-R_gb.T @ t_gb)

        R_t2c.append(cv2.Rodrigues(np.array(s["rvec_target2cam"]))[0])
        t_t2c.append(np.array(s["tvec_target2cam"]).reshape(3, 1))

    R_c2b, t_c2b = cv2.calibrateHandEye(
        R_b2g, t_b2g, R_t2c, t_t2c, method=cv2.CALIB_HAND_EYE_TSAI
    )

    T_c2b = np.eye(4)
    T_c2b[:3, :3] = R_c2b
    T_c2b[:3, 3] = t_c2b.ravel()

    print("\ncamera -> base transform (4x4, metres):")
    print(np.array2string(T_c2b, precision=5, suppress_small=True))
    print(f"\ncamera position in base frame: "
          f"{np.round(t_c2b.ravel() * 1000, 1)} mm")

    # ---- residual ----------------------------------------------------
    # The board origin, expressed in the base frame, should be the same
    # rigid offset from the flange in every sample. Its scatter is the
    # calibration residual.
    pts = []
    for s, T_g2b in zip(samples, T_g2b_all):
        T_t2c = np.eye(4)
        T_t2c[:3, :3] = cv2.Rodrigues(np.array(s["rvec_target2cam"]))[0]
        T_t2c[:3, 3] = np.array(s["tvec_target2cam"])
        T_t2b = T_c2b @ T_t2c                 # board in base frame
        T_t2g = np.linalg.inv(T_g2b) @ T_t2b  # board in flange frame
        pts.append(T_t2g[:3, 3])

    pts = np.array(pts)
    centroid = pts.mean(axis=0)
    resid = np.linalg.norm(pts - centroid, axis=1)
    print(f"\nresidual over {len(pts)} poses:")
    print(f"  RMS  {np.sqrt((resid ** 2).mean()) * 1000:6.2f} mm")
    print(f"  mean {resid.mean() * 1000:6.2f} mm")
    print(f"  max  {resid.max() * 1000:6.2f} mm")
    print(f"  board origin in flange frame: {np.round(centroid * 1000, 1)} mm")

    if np.sqrt((resid ** 2).mean()) * 1000 > 5:
        print("\n  RMS above 5 mm -- likely causes: not enough ORIENTATION")
        print("  variation between poses, a board that shifted mid-capture,")
        print("  or a wrong SQUARE_LENGTH_M.")

    with open(RESULT_FILE, "w") as f:
        json.dump({
            "T_cam2base": T_c2b.tolist(),
            "residual_rms_mm": float(np.sqrt((resid ** 2).mean()) * 1000),
            "n_poses": len(pts),
        }, f, indent=2)
    print(f"\nwrote {RESULT_FILE}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "board"
    if mode == "board":
        make_board()
    elif mode == "collect":
        collect()
    elif mode == "solve":
        solve(*sys.argv[2:])
    else:
        print(__doc__)